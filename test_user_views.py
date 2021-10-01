import os
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from app import app, CURR_USER_KEY

from unittest import TestCase
from models import db, connect_db, Follows, Likes, User, Message

app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql://postgres:Ob1wankenobi@localhost/warbler_tests'))

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
        the session and redirects to '/'"""
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess["curr_user"] = 1
            self.assertEqual(sess.get("curr_user"), 1)
            request = client.get('/logout', follow_redirects=True)
            self.assertEqual(request.status_code, 200)
            response = request.get_data(as_text=True)
            self.assertIn('<h4>New to Warbler?</h4>', response)
            with client.session_transaction() as sess:
                self.assertIsNone(sess.get("curr_user"))