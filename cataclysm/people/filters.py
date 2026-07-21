from dataclasses import dataclass, field

from django.db.models import Q, QuerySet

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

    @classmethod
    def from_querydict(cls, params):
        requested_order = params.get('order_by', 'name')
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
        )


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
