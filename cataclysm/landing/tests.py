from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase
from django.urls import reverse


User = get_user_model()


class PasswordResetFlowTests(TestCase):
    """End-to-end tests for the password-reset feature."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='resetuser',
            email='resetuser@example.com',
            password='OldSecurePass1!',
        )

    # ------------------------------------------------------------------
    # Page accessibility
    # ------------------------------------------------------------------

    def test_password_reset_form_page_returns_200(self):
        response = self.client.get(reverse('password_reset'))
        self.assertEqual(response.status_code, 200)

    def test_password_reset_done_page_returns_200(self):
        response = self.client.get(reverse('password_reset_done'))
        self.assertEqual(response.status_code, 200)

    def test_password_reset_complete_page_returns_200(self):
        response = self.client.get(reverse('password_reset_complete'))
        self.assertEqual(response.status_code, 200)

    def test_login_page_returns_200(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    # ------------------------------------------------------------------
    # Non-enumeration: same response whether email exists or not
    # ------------------------------------------------------------------

    def test_reset_request_with_existing_email_redirects_to_done(self):
        response = self.client.post(
            reverse('password_reset'),
            {'email': 'resetuser@example.com'},
        )
        self.assertRedirects(response, reverse('password_reset_done'))

    def test_reset_request_with_unknown_email_also_redirects_to_done(self):
        """Must NOT reveal whether an account exists for that email."""
        response = self.client.post(
            reverse('password_reset'),
            {'email': 'nobody@example.com'},
        )
        self.assertRedirects(response, reverse('password_reset_done'))

    # ------------------------------------------------------------------
    # Email dispatch
    # ------------------------------------------------------------------

    def test_reset_request_sends_email_to_known_address(self):
        self.client.post(
            reverse('password_reset'),
            {'email': 'resetuser@example.com'},
        )
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('resetuser@example.com', mail.outbox[0].to)

    def test_reset_request_sends_no_email_for_unknown_address(self):
        self.client.post(
            reverse('password_reset'),
            {'email': 'nobody@example.com'},
        )
        self.assertEqual(len(mail.outbox), 0)

    def test_reset_email_contains_reset_link(self):
        self.client.post(
            reverse('password_reset'),
            {'email': 'resetuser@example.com'},
        )
        self.assertGreater(len(mail.outbox), 0)
        body = mail.outbox[0].body
        self.assertIn('/accounts/reset/', body)

    # ------------------------------------------------------------------
    # Token confirmation & password change
    # ------------------------------------------------------------------

    def _request_reset_and_get_confirm_url(self):
        """Helper: trigger reset, extract confirm URL from the outbox."""
        self.client.post(
            reverse('password_reset'),
            {'email': 'resetuser@example.com'},
        )
        body = mail.outbox[0].body
        # The confirm URL line looks like: http://testserver/accounts/reset/<uid>/<token>/
        for line in body.splitlines():
            line = line.strip()
            if '/accounts/reset/' in line:
                # Strip protocol+host so we can use the test client
                path = line.split('testserver', 1)[-1]
                return path
        return None

    def test_valid_reset_link_shows_set_password_form(self):
        url = self._request_reset_and_get_confirm_url()
        self.assertIsNotNone(url)
        # Django redirects the first GET to a session-stored URL
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Set New Password')

    def test_successful_password_change_via_reset_link(self):
        url = self._request_reset_and_get_confirm_url()
        self.assertIsNotNone(url)
        # Follow the initial redirect to get the session-keyed confirm URL
        response = self.client.get(url, follow=True)
        confirm_url = response.redirect_chain[-1][0] if response.redirect_chain else url
        response = self.client.post(
            confirm_url,
            {
                'new_password1': 'NewSecurePass2@',
                'new_password2': 'NewSecurePass2@',
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewSecurePass2@'))

    def test_invalid_token_shows_error_message(self):
        response = self.client.get(
            reverse('password_reset_confirm', kwargs={'uidb64': 'bad', 'token': 'bad-token'}),
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'invalid or has expired')

    def test_expired_token_cannot_be_reused(self):
        """Using a valid link twice must fail on the second attempt."""
        url = self._request_reset_and_get_confirm_url()
        self.assertIsNotNone(url)
        response = self.client.get(url, follow=True)
        confirm_url = response.redirect_chain[-1][0] if response.redirect_chain else url
        # First use – should succeed
        self.client.post(
            confirm_url,
            {'new_password1': 'NewSecurePass2@', 'new_password2': 'NewSecurePass2@'},
        )
        # Second use – token is now consumed; attempt on original URL must fail
        response2 = self.client.get(url, follow=True)
        self.assertContains(response2, 'invalid or has expired')

