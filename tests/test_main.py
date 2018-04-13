# Copyright 2015 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import sys
import os.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, 'code')))

import os
import main
from code.user import *
import unittest

from google.appengine.api import users
from google.appengine.ext import testbed


class MainTest(unittest.TestCase):
    def loginUser(self, email="ahg2142@columbia.edu", id="666", is_admin=False):
        self.testbed.setup_env(
            user_email=email,
            user_id=id,
            user_is_admin='1' if is_admin else '0',
            overwrite=True)

    def testLogin(self):
        self.assertFalse(users.get_current_user())
        self.loginUser()
        self.assertEquals(users.get_current_user().email(), 'ahg2142@columbia.edu')
        self.loginUser(is_admin=True)
        self.assertTrue(users.is_current_user_admin())

    def check_culunch(self, rv):
        assert("cu@lunch" in rv.data.lower())

    def test_registered_user(self):
        assert(main.check_registered_user("ahg2142"))

    def setUp(self):
        self.app = main.app.test_client()

        # for mocking the users API
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_user_stub()

    def test_index(self):
        # make sure it stays on the landing page for a non-registered user


        # test redirecting for a logged-in user who has an account
        self.loginUser()
        rv = self.app.get('/', follow_redirects=True)
        # make sure it redirects on a logged-in user
        assert("listings" in rv.data.lower())


    def test_listform(self):
        self.loginUser()
        rv = self.app.get("/listform")
        self.check_culunch(rv)

    def tearDown(self):
        self.testbed.deactivate()

# user creation validation
class ValidTest(unittest.TestCase):

    def test_form(self):
        # good
        form = Form("Shelley", "S", "sks2209", "school", "year", "interests")
        self.assertTrue(form.form_input_valid())

        # good
        form = Form("Shelley", "S", "sks2209", "school", "year", "interests")
        self.assertTrue(form.form_input_valid())

        # good
        form = Form("Shelley", "S", "sks2209", "school", "year", "interests")
        self.assertTrue(form.form_input_valid())

        # no name
        form = Form("", "S", "sks2209", "school", "year", "interests")
        self.assertTrue((form.form_input_valid() == (False, 'empty')))

        # no last
        form = Form("Shelley", "", "sks2209", "school", "year", "interests")
        self.assertTrue((form.form_input_valid () == (False, 'empty')))

        # no uni
        form = Form("Shelley", "S", "", "school", "year", "interests")
        self.assertTrue((form.form_input_valid() == (False, 'empty')))



if __name__ == '__main__':
    unittest.main()