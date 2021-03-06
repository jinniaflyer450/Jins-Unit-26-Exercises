import os
from flask import Flask, request, session
from flask_sqlalchemy import SQLAlchemy
from app import app, CURR_USER_KEY

from unittest import TestCase
from models import db, connect_db, Follows, Likes, User, Message

app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql://postgres:Ob1wankenobi@localhost/warbler_tests'))
app.config['WTF_CSRF_ENABLED']=False

class WarblerUserViewsTests(TestCase):
    """Tests for the user views for Warbler."""
    @classmethod
    def setUpCls(cls):
        """Sets up the database before all tests."""
        db.drop_all()
        db.session.commit()

    def setUp(self):
        """Sets up the database before each test."""
        db.create_all()
        db.session.commit()
        exec(open('seed.py').read())
        db.session.commit()
    
    def tearDown(self):
        """Resets the database after each test."""
        db.session.close_all()
        db.drop_all()
        db.session.commit()
    
    def test_logout(self):
        """Tests to make sure that the '/logout' view function removes any current user from
        the session and redirects to '/' with the flashed message 'Goodbye!'"""
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = 1
            request = client.get('/logout', follow_redirects=True)
            self.assertEqual(request.status_code, 200)
            response = request.get_data(as_text=True)
            self.assertIn('<h4>New to Warbler?</h4>', response)
            with client.session_transaction() as sess:
                self.assertIsNone(sess.get(CURR_USER_KEY))
            self.assertIn('<div class="alert alert-success">Goodbye!</div>', response)
    
    def test_users_show_other(self):
        """Tests that the users_show view function displays a details page for the user in the URL with
        all relevant components when no user is logged in."""
        with app.test_client() as client:
            request = client.get('/users/1', follow_redirects=True)
            self.assertEqual(request.status_code, 200)
            response = request.get_data(as_text=True)

            #Elements that should be in the template--header image, part of profile image, 
            #part of user link for messages, location, bio.
            self.assertIn('class= "img-fluid w-100 h-100"', response)
            self.assertIn('alt="Image for tuckerdiane', response)
            self.assertIn('<a href="/users/1">', response)
            self.assertIn('Garrettburgh', response)
            self.assertIn('Movement later fund employee site turn.', response)

            #Elements that should not be in the template: options to edit or delete profile.
            self.assertNotIn('Edit Profile', response)
            self.assertNotIn('Delete Profile', response)

            #Elements that should not be in the template: options to follow or unfollow.
            self.assertNotIn('Unfollow', response)
            self.assertNotIn('users/follow/', response)
    
    def test_users_show_follower(self):
        """Tests that the users_show view function displays a details page for the user in the URL with
        all relevant components when someone who follows the user is logged in."""
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = 3
            request = client.get('/users/1', follow_redirects=True)
            self.assertEqual(request.status_code, 200)
            response = request.get_data(as_text=True)

            #Elements that should be in the template--header image, part of profile image, 
            #part of user link for messages, bio, location.
            self.assertIn('class= "img-fluid w-100 h-100"', response)
            self.assertIn('alt="Image for tuckerdiane', response)
            self.assertIn('<a href="/users/1">', response)
            self.assertIn('Garrettburgh', response)
            self.assertIn('Movement later fund employee site turn.', response)

            #Elements that should be in the template--option to unfollow user.
            self.assertIn('Unfollow', response)

            #Elements that should not be in the template: options to edit/delete profile and
            #options to follow.
            self.assertNotIn('users/follow/', response)
            self.assertNotIn('Edit Profile', response)
            self.assertNotIn('Delete Profile', response)

    def test_users_show_not_follower(self):
        """Tests that the users_show view function displays a details page for the user in the URL with
        all relevant components when someone who doesn't follow the user is logged in."""
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = 5
            request = client.get('/users/1', follow_redirects=True)
            self.assertEqual(request.status_code, 200)
            response = request.get_data(as_text=True)

            #Elements that should be in the template--header image, part of profile image, 
            #part of user link for messages, bio, location.
            self.assertIn('class= "img-fluid w-100 h-100"', response)
            self.assertIn('alt="Image for tuckerdiane', response)
            self.assertIn('<a href="/users/1">', response)
            self.assertIn('Garrettburgh', response)
            self.assertIn('Movement later fund employee site turn.', response)

            #Elements that should be in the template--option to follow user.
            self.assertIn('/users/follow', response)

            #Elements that should not be in the template: options to edit/delete profile and
            #options to unfollow.
            self.assertNotIn('Unfollow', response)
            self.assertNotIn('Edit Profile', response)
            self.assertNotIn('Delete Profile', response)
    
    def test_users_show_self(self):
        """Tests that the users_show view function displays a details page for hte user in the URL with
        all relevant components when the user in the URL is logged in."""
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = 1
            request = client.get('/users/1', follow_redirects=True)
            self.assertEqual(request.status_code, 200)
            response = request.get_data(as_text=True)

            #Elements that should be in the template--header image, part of profile image, 
            #part of user link for messages, bio, location.
            self.assertIn('class= "img-fluid w-100 h-100"', response)
            self.assertIn('alt="Image for tuckerdiane', response)
            self.assertIn('<a href="/users/1">', response)
            self.assertIn('Garrettburgh', response)
            self.assertIn('Movement later fund employee site turn.', response)

            #Elements that should be in the template--options to edit/delete profile.
            self.assertIn('Edit Profile', response)
            self.assertIn('Delete Profile', response)
            
            #Elements that should not be in the template: options to follow profile and
            #options to unfollow.
            self.assertNotIn('/users/follow', response)
            self.assertNotIn('Unfollow', response)
    
    def test_users_followers_no_login(self):
        """Tests that the users_followers view function redirects to '/' with the appropriate
        flashed message if no user is logged in."""
        with app.test_client() as client:
            request = client.get('/users/1/followers', follow_redirects=True)
            self.assertEqual(request.status_code, 200)
            response = request.get_data(as_text=True)
            self.assertIn("Access unauthorized", response)
            self.assertIn("<h4>New to Warbler?</h4>", response)
    
    def test_users_followers_login(self):
        """Tests that the users_followers view function renders 'followers.html' with all
        relevant information if a user is logged in."""
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = 5
            request = client.get('/users/1/followers', follow_redirects=True)
            self.assertEqual(request.status_code, 200)
            response = request.get_data(as_text=True)

            #Info from user 3, a follower of user 1.
            self.assertIn('<a href="/users/3" class="card-link">', response)
            self.assertIn('Maybe key community young ahead.', response)

            #General components.
            self.assertIn('Follow', response)
            self.assertIn('Unfollow', response)
    
    def test_show_following_no_login(self):
        """Tests that the show_following view function redirects to '/' with the appropriate flashed
        message if no user is logged in."""
        with app.test_client() as client:
            request = client.get('/users/3/following', follow_redirects=True)
            self.assertEqual(request.status_code, 200)
            response = request.get_data(as_text=True)
            self.assertIn("Access unauthorized", response)
            self.assertIn("<h4>New to Warbler?</h4>", response)
    
    def test_show_following_login(self):
        """Tests that the show_following view function renders 'following.html' with all relevant
        information if a user is logged in."""
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = 5
            request = client.get('/users/3/following', follow_redirects=True)
            self.assertEqual(request.status_code, 200)
            response = request.get_data(as_text=True)

            #Info from user 1, a user that user 3 is following.
            self.assertIn('<a href="/users/1" class="card-link">', response)
            self.assertIn('Movement later fund employee site turn.', response)

            #General components.
            self.assertIn('Follow', response)
            self.assertIn('Unfollow', response)
    
    def test_list_users_no_login_all(self):
        """Tests that the list_users view function renders 'index.html' with all relevant
        information if there is no query string and no user is logged in."""
        with app.test_client() as client:
            request = client.get('/users', follow_redirects=True)
            self.assertEqual(request.status_code, 200)
            response = request.get_data(as_text=True)

            #Info from user 1, who should appear in results.
            self.assertIn('<a href="/users/1" class="card-link">', response)
            self.assertIn('Movement later fund employee site turn.', response)

            #Info that should not appear in the template--no user logged in.
            self.assertNotIn('Follow', response)
            self.assertNotIn('Unfollow', response)
    
    def test_list_users_no_login_query(self):
        """Tests that the list_users view function renders 'index.html' with all relevant
        information if there is a query string and no user is logged in."""
        with app.test_client() as client:
            request = client.get('/users?q=tuckerdiane', follow_redirects=True)
            self.assertEqual(request.status_code, 200)
            response = request.get_data(as_text=True)

            #Info from user 1, who should appear in results.
            self.assertIn('<a href="/users/1" class="card-link">', response)
            self.assertIn('Movement later fund employee site turn.', response)

            #Info from user 3, who should not appear in results.
            self.assertNotIn('<a href="/users/3" class="card-link">', response)
            self.assertNotIn('Maybe key community young ahead.', response)

            #Info that should not appear in the template--no user logged in.
            self.assertNotIn('Follow', response)
            self.assertNotIn('Unfollow', response)
    
    def test_list_users_login(self):
        """Tests that the list_users view function renders 'index.html' with all relevant
        information if there is no query string and a user is logged in."""
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = 5
            request = client.get('/users', follow_redirects=True)
            self.assertEqual(request.status_code, 200)
            response = request.get_data(as_text=True)

            #Info from user 1, who should appear in results.
            self.assertIn('<a href="/users/1" class="card-link">', response)
            self.assertIn('Movement later fund employee site turn.', response)

            #Info that should appear in the template--user logged in.
            self.assertIn('Follow', response)
            self.assertIn('Unfollow', response)
    
    def test_list_users_login_query(self):
        """Tests that the list_users view function renders 'index.html' with all relevant
        information if there is a query string and a user is logged in."""
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = 3
            request = client.get('/users?q=tuckerdiane', follow_redirects=True)
            self.assertEqual(request.status_code, 200)
            response = request.get_data(as_text=True)

            #Info from user 1, who should appear in results.
            self.assertIn('<a href="/users/1" class="card-link">', response)
            self.assertIn('Movement later fund employee site turn.', response)

            #Info from user 5, who should not appear in results.
            self.assertNotIn('<a href="/users/5" class="card-link">', response)
            self.assertNotIn('Cell itself institution couple should.', response)
            
            #Info that should appear in the template--user logged in, one result who user is following.
            self.assertIn('Unfollow', response)

            #Info that should not appear in the template--user logged in, one result who user is following.
            self.assertNotIn('Follow', response)
    
    def test_list_users_no_users(self):
        """Tests that the list_users view function renders 'index.html' with all relevant
        information if there is a query string that excludes all users."""
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = 3
            request = client.get('/users?q=adjiosaiojpaoieht', follow_redirects=True)
            self.assertEqual(request.status_code, 200)
            response = request.get_data(as_text=True)

            #Info from user 5, who should not appear in results.
            self.assertNotIn('<a href="/users/5" class="card-link">', response)
            self.assertNotIn('Cell itself institution couple should.', response)

            #Info that should not appear in the template--no users displayed.
            self.assertNotIn('Follow', response)
            self.assertNotIn('Unfollow', response)

            #Info that should appear in the template--no users found.
            self.assertIn('<h3>Sorry, no users found</h3>', response)
    
    def test_profile_no_login(self):
        """Tests that the 'profile' view function returns a redirect to '/' if no
        user is logged in."""

        with app.test_client() as client:
            request = client.get('/users/profile', follow_redirects=True)
            self.assertEqual(request.status_code, 200)
            response = request.get_data(as_text=True)

            self.assertIn('<h4>New to Warbler?</h4>', response)
            self.assertIn('Access unauthorized', response)
    
    def test_profile_login_get(self):
        """Tests the the 'profile' view function returns 'edit.html' on a GET request with
        details for the appropriate user if a user is logged in."""

        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = 1
            request = client.get('/users/profile', follow_redirects=True)
            self.assertEqual(request.status_code, 200)
            response = request.get_data(as_text=True)

            self.assertIn('<h2 class="join-message">Edit Your Profile.</h2>', response)
            self.assertIn('<a href="/users/1" class="btn btn-outline-secondary">Cancel</a>', response)
            self.assertIn('tuckerdiane', response)
            self.assertNotIn('CSRF', response)