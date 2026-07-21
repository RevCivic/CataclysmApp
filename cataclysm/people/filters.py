from dataclasses import dataclass, field

from django.db.models import Q, QuerySet
from django.http import QueryDict

from .models import Person


SORT_FIELDS = {
    'id': 'id',
    '-id': '-id',
    'name': 'name',
    '-name': '-name',
    'age': 'age',
    '-age': '-age',
    'sex': 'sex',
    '-sex': '-sex',
    'species': 'species__species_name',
    '-species': '-species__species_name',
    'faction': 'faction__name',
    '-faction': '-faction__name',
    'rank': 'rank',
    '-rank': '-rank',
    'position': 'position',
    '-position': '-position',
    'hidden': 'hidden',
    '-hidden': '-hidden',
}

PERSON_COLUMNS = {
    'id': 'ID',
    'name': 'Name',
    'age': 'Age',
    'sex': 'Sex',
    'species': 'Species',
    'faction': 'Faction',
    'rank': 'Rank',
    'position': 'Position',
    'assignments': 'Assignments',
    'traits': 'Traits',
    'tags': 'Tags',
    'picture': 'Picture',
}
DEFAULT_PERSON_COLUMNS = list(PERSON_COLUMNS)


def _integer_values(values):
    return [int(value) for value in values if str(value).isdigit()]


@dataclass
class PersonFilterState:
    query: str = ''
    tag_ids: list[int] = field(default_factory=list)
    trait_ids: list[int] = field(default_factory=list)
    capability_ids: list[int] = field(default_factory=list)
    species_ids: list[int] = field(default_factory=list)
    unit_ids: list[int] = field(default_factory=list)
    statuses: list[str] = field(default_factory=list)
    rank: str = ''
    role: str = ''
    location: str = ''
    order_by: str = 'name'
    columns: list[str] = field(default_factory=lambda: DEFAULT_PERSON_COLUMNS.copy())

    @classmethod
    def from_querydict(cls, params):
        requested_order = params.get('order_by', 'name')
        requested_columns = params.getlist('column')
        return cls(
            query=params.get('q', '').strip(),
            tag_ids=_integer_values(params.getlist('tag')),
            trait_ids=_integer_values(params.getlist('trait')),
            capability_ids=_integer_values(params.getlist('capability')),
            species_ids=_integer_values(params.getlist('species')),
            unit_ids=_integer_values(params.getlist('unit')),
            statuses=[value.strip() for value in params.getlist('status') if value.strip()],
            rank=params.get('rank', '').strip(),
            role=params.get('role', '').strip(),
            location=params.get('location', '').strip(),
            order_by=requested_order if requested_order in SORT_FIELDS else 'name',
            columns=(
                [column for column in requested_columns if column in PERSON_COLUMNS]
                if requested_columns
                else DEFAULT_PERSON_COLUMNS.copy()
            ),
        )

    def as_dict(self):
        return {
            'q': self.query,
            'tag': self.tag_ids,
            'trait': self.trait_ids,
            'capability': self.capability_ids,
            'species': self.species_ids,
            'unit': self.unit_ids,
            'status': self.statuses,
            'rank': self.rank,
            'role': self.role,
            'location': self.location,
            'order_by': self.order_by,
        }

    def as_query_string(self):
        params = QueryDict(mutable=True)
        for key, value in self.as_dict().items():
            if isinstance(value, list):
                params.setlist(key, [str(item) for item in value])
            elif value:
                params[key] = str(value)
        if self.columns != DEFAULT_PERSON_COLUMNS:
            params.setlist('column', self.columns)
        return params.urlencode()

    @classmethod
    def from_dict(cls, data, columns=None):
        params = QueryDict(mutable=True)
        if not isinstance(data, dict):
            return cls()
        for key, value in data.items():
            if isinstance(value, list):
                params.setlist(key, [str(item) for item in value])
            elif isinstance(value, (str, int)):
                params[key] = str(value)
        if isinstance(columns, list):
            params.setlist('column', [str(column) for column in columns])
        return cls.from_querydict(params)


def filter_people(queryset: QuerySet[Person], state: PersonFilterState, include_hidden=False):
    if not include_hidden:
        queryset = queryset.filter(hidden=False)

    if state.query:
        queryset = queryset.filter(
            Q(name__icontains=state.query)
            | Q(aliases__name__icontains=state.query)
            | Q(species__species_name__icontains=state.query)
            | Q(assignments__role__icontains=state.query)
            | Q(assignments__unit__name__icontains=state.query)
            | Q(profile_facts__value__icontains=state.query)
        )
    if state.tag_ids:
        queryset = queryset.filter(tags__id__in=state.tag_ids)
    if state.species_ids:
        queryset = queryset.filter(species_id__in=state.species_ids)
    if state.unit_ids:
        queryset = queryset.filter(assignments__unit_id__in=state.unit_ids)
    if state.statuses:
        queryset = queryset.filter(assignments__status__in=state.statuses)
    if state.rank:
        queryset = queryset.filter(Q(rank__icontains=state.rank) | Q(assignments__rank__icontains=state.rank))
    if state.role:
        queryset = queryset.filter(Q(position__icontains=state.role) | Q(assignments__role__icontains=state.role))
    if state.location:
        queryset = queryset.filter(
            Q(location__icontains=state.location)
            | Q(profile_facts__key='origin', profile_facts__value__icontains=state.location)
        )

    # Repeated trait/capability parameters use AND semantics: every selected
    # value must be present on the character.
    for trait_id in state.trait_ids:
        queryset = queryset.filter(traits__id=trait_id)
    for capability_id in state.capability_ids:
        queryset = queryset.filter(capabilities__capability_id=capability_id)

    return queryset.order_by(SORT_FIELDS[state.order_by], 'id').distinct()
