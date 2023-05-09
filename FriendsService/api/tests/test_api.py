from rest_framework.test import APITestCase

create_user_url = '/api/create-user'
login_url = '/api/token'
refresh_url = '/api/token/refresh'
send_friend_request_url = '/api/friends/send-request'
respond_to_friend_request_url = '/api/friends/respond-to-request'
revoke_friend_request_url = '/api/friends/revoke-request'
get_incoming_requests_url = '/api/friends/get-incoming-requests'
get_outgoing_requests_url = '/api/friends/get-outgoing-requests'
get_friends_url = '/api/friends/get-friends'
remove_friend_url = '/api/friends/remove-friend'


def get_status_with_user_url(username):
    return f'/api/friends/get-status-with-user/{username}'


username1 = 'user1'
username2 = 'user2'
username3 = 'user3'
password = '123123'


class FriendsServiceApiTestCase(APITestCase):
    def test_create_user(self):
        # invalid request data
        response = self.client.post(create_user_url, {
            'username': '',
            'password': '123123'
        })
        self.assertEqual(response.status_code, 400)

        # invalid request data
        response = self.client.post(create_user_url, {
            'username': username2,
            'password': ''
        })
        self.assertEqual(response.status_code, 400)

        # valid login data
        response = self.client.post(create_user_url, {
            'username': username1,
            'password': '123123'
        })
        self.assertEqual(response.status_code, 201)

        # user already exist
        response = self.client.post(create_user_url, {
            'username': username1,
            'password': '123123'
        })
        self.assertEqual(response.status_code, 409)

    def test_authentication(self):
        self.create_users([username1])

        # invalid login data
        response = self.client.post(login_url, {
            'username': username1 + '1',
            'password': password
        })
        self.assertEqual(response.status_code, 401)

        # invalid login data
        response = self.client.post(login_url, {
            'username': username1,
            'password': password + '1'
        })
        self.assertEqual(response.status_code, 401)

        # invalid request data
        response = self.client.post(login_url, {
            'username': username1
        })
        self.assertEqual(response.status_code, 400)

        # valid login data
        response = self.client.post(login_url, {
            'username': username1,
            'password': password
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('refresh', response.data.keys())
        self.assertIn('access', response.data.keys())
        refresh_token = response.data['refresh']

        # invalid request data
        response = self.client.post(refresh_url, {
            'refresh_': refresh_token,
        })
        self.assertEqual(response.status_code, 400)

        # invalid refresh token
        response = self.client.post(refresh_url, {
            'refresh': refresh_token+'1',
        })
        self.assertEqual(response.status_code, 401)

        # valid refresh token
        response = self.client.post(refresh_url, {
            'refresh': refresh_token,
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('refresh', response.data.keys())
        self.assertIn('access', response.data.keys())

    def test_friend_request(self):
        access_tokens = self.create_users([username1, username2])

        # send friend request without authorization header
        response = self.client.post(send_friend_request_url, {
            'username': username1
        })
        self.assertEqual(response.status_code, 401)

        # invalid data
        response = self.client.post(send_friend_request_url, {
            'username_': username1
        }, headers={'Authorization': 'Bearer ' + access_tokens[0]})
        self.assertEqual(response.status_code, 400)

        # user1 send friend request to himself
        response = self.client.post(send_friend_request_url, {
            'username': username1
        }, headers={'Authorization': 'Bearer ' + access_tokens[0]})
        self.assertEqual(response.status_code, 400)

        # user1 send friend request to user that is does not exist
        response = self.client.post(send_friend_request_url, {
            'username': 'user4'
        }, headers={'Authorization': 'Bearer ' + access_tokens[0]})
        self.assertEqual(response.status_code, 404)

        # user1 send friend request to user2
        response = self.client.post(send_friend_request_url, {
            'username': username2
        }, headers={'Authorization': 'Bearer ' + access_tokens[0]})
        self.assertEqual(response.status_code, 201)

        # user1 again send friend request to user2
        response = self.client.post(send_friend_request_url, {
            'username': username2
        }, headers={'Authorization': 'Bearer ' + access_tokens[0]})
        self.assertEqual(response.status_code, 200)

        # user2 send friend request to user1, accept automatically
        response = self.client.post(send_friend_request_url, {
            'username': username1
        }, headers={'Authorization': 'Bearer ' + access_tokens[1]})
        self.assertEqual(response.status_code, 202)

        # user1 send friend request to user2, but they are already friends
        response = self.client.post(send_friend_request_url, {
            'username': username2
        }, headers={'Authorization': 'Bearer ' + access_tokens[0]})
        self.assertEqual(response.status_code, 400)

    def test_respond_to_friend_request(self):
        access_tokens = self.create_users([username1, username2])

        # accept friend request without authorization header
        response = self.client.post(respond_to_friend_request_url, {
            'username': username2,
            'action': True
        })
        self.assertEqual(response.status_code, 401)

        # invalid request data
        response = self.client.post(respond_to_friend_request_url, {
            'action': True
        }, headers={'Authorization': 'Bearer ' + access_tokens[0]})
        self.assertEqual(response.status_code, 400)

        # accept friend request that does not exist
        response = self.client.post(respond_to_friend_request_url, {
            'username': username2,
            'action': True
        }, headers={'Authorization': 'Bearer ' + access_tokens[0]})
        self.assertEqual(response.status_code, 404)

        # accept friend request from user that does not exist
        response = self.client.post(respond_to_friend_request_url, {
            'username': username3,
            'action': True
        }, headers={'Authorization': 'Bearer ' + access_tokens[0]})
        self.assertEqual(response.status_code, 404)

        # user1 send friend request to user2
        response = self.client.post(send_friend_request_url, {
            'username': username2
        }, headers={'Authorization': 'Bearer ' + access_tokens[0]})
        self.assertEqual(response.status_code, 201)

        # user2 refuse friend request from user1
        response = self.client.post(respond_to_friend_request_url, {
            'username': username1,
            'action': False
        }, headers={'Authorization': 'Bearer ' + access_tokens[1]})
        self.assertEqual(response.status_code, 200)

        # user2 send friend request to user1
        response = self.client.post(send_friend_request_url, {
            'username': username1
        }, headers={'Authorization': 'Bearer ' + access_tokens[1]})
        self.assertEqual(response.status_code, 201)

        # user1 accept friend request from user2
        response = self.client.post(respond_to_friend_request_url, {
            'username': username2,
            'action': True
        }, headers={'Authorization': 'Bearer ' + access_tokens[0]})
        self.assertEqual(response.status_code, 202)

    def test_revoke_request(self):
        access_tokens = self.create_users([username1, username2])

        # revoke friend request without authorization header
        response = self.client.post(revoke_friend_request_url, {
            'username': username2
        })
        self.assertEqual(response.status_code, 401)

        # invalid request data
        response = self.client.post(revoke_friend_request_url, {
            'username_': username2
        }, headers={'Authorization': 'Bearer ' + access_tokens[0]})
        self.assertEqual(response.status_code, 400)

        # user1 revoke friend request from user that does not exist
        response = self.client.post(revoke_friend_request_url, {
            'username': username3
        }, headers={'Authorization': 'Bearer ' + access_tokens[0]})
        self.assertEqual(response.status_code, 404)

        # user1 revoke friend request that does not exist
        response = self.client.post(revoke_friend_request_url, {
            'username': username2
        }, headers={'Authorization': 'Bearer ' + access_tokens[0]})
        self.assertEqual(response.status_code, 404)

        # user1 send friend request to user2
        response = self.client.post(send_friend_request_url, {
            'username': username2
        }, headers={'Authorization': 'Bearer ' + access_tokens[0]})
        self.assertEqual(response.status_code, 201)

        # user1 revoke friend request to user2
        response = self.client.post(revoke_friend_request_url, {
            'username': username2
        }, headers={'Authorization': 'Bearer ' + access_tokens[0]})
        self.assertEqual(response.status_code, 200)

        # user2 accept friend request from user1 (request does not exist already)
        response = self.client.post(respond_to_friend_request_url, {
            'username': username1,
            'action': True
        }, headers={'Authorization': 'Bearer ' + access_tokens[1]})
        self.assertEqual(response.status_code, 404)

    def test_get_list_of_requests_and_friends(self):
        access_tokens = self.create_users([username1, username2, username3])

        # user1 send friend request to user2, user3
        response = self.client.post(send_friend_request_url, {
            'username': username2
        }, headers={'Authorization': 'Bearer ' + access_tokens[0]})
        self.assertEqual(response.status_code, 201)
        response = self.client.post(send_friend_request_url, {
            'username': username3
        }, headers={'Authorization': 'Bearer ' + access_tokens[0]})
        self.assertEqual(response.status_code, 201)

        # user2 send friend request to user3
        response = self.client.post(send_friend_request_url, {
            'username': username3
        }, headers={'Authorization': 'Bearer ' + access_tokens[1]})
        self.assertEqual(response.status_code, 201)

        # get list of outgoing friend requests for user1
        response = self.client.get(get_outgoing_requests_url,
                                   headers={'Authorization': 'Bearer ' + access_tokens[0]})
        self.assertEqual(response.status_code, 200)
        self.assertIn('usernames', response.data.keys())
        self.assertListEqual(response.data['usernames'], [username2, username3])

        # get list of incoming friend requests without authorization header
        response = self.client.get(get_incoming_requests_url)
        self.assertEqual(response.status_code, 401)

        # get list of outgoing friend requests without authorization header
        response = self.client.get(get_outgoing_requests_url)
        self.assertEqual(response.status_code, 401)

        # get list of friends without authorization header
        response = self.client.get(get_friends_url)
        self.assertEqual(response.status_code, 401)

        # get list of incoming friend requests for user3
        response = self.client.get(get_incoming_requests_url,
                                   headers={'Authorization': 'Bearer ' + access_tokens[2]})
        self.assertEqual(response.status_code, 200)
        self.assertIn('usernames', response.data.keys())
        self.assertListEqual(response.data['usernames'], [username1, username2])

        # user3 refuse friend request from user1
        response = self.client.post(respond_to_friend_request_url, {
            'username': username1,
            'action': False
        }, headers={'Authorization': 'Bearer ' + access_tokens[2]})
        self.assertEqual(response.status_code, 200)

        # get list of incoming friend requests for user3
        response = self.client.get(get_incoming_requests_url,
                                   headers={'Authorization': 'Bearer ' + access_tokens[2]})
        self.assertEqual(response.status_code, 200)
        self.assertIn('usernames', response.data.keys())
        self.assertListEqual(response.data['usernames'], [username2])

        # get list of outgoing friend requests for user1
        response = self.client.get(get_outgoing_requests_url,
                                   headers={'Authorization': 'Bearer ' + access_tokens[0]})
        self.assertEqual(response.status_code, 200)
        self.assertIn('usernames', response.data.keys())
        self.assertListEqual(response.data['usernames'], [username2])

        # user3 send request to user2, accept automatically
        response = self.client.post(send_friend_request_url, {
            'username': username2
        }, headers={'Authorization': 'Bearer ' + access_tokens[2]})
        self.assertEqual(response.status_code, 202)

        # get list of friends for user3
        response = self.client.get(get_friends_url,
                                   headers={'Authorization': 'Bearer ' + access_tokens[2]})
        self.assertEqual(response.status_code, 200)
        self.assertIn('usernames', response.data.keys())
        self.assertListEqual(response.data['usernames'], [username2])

        # get list of friends for user2
        response = self.client.get(get_friends_url,
                                   headers={'Authorization': 'Bearer ' + access_tokens[1]})
        self.assertEqual(response.status_code, 200)
        self.assertIn('usernames', response.data.keys())
        self.assertListEqual(response.data['usernames'], [username3])

        # get list of outgoing friend requests for user2
        response = self.client.get(get_outgoing_requests_url,
                                   headers={'Authorization': 'Bearer ' + access_tokens[1]})
        self.assertEqual(response.status_code, 200)
        self.assertIn('usernames', response.data.keys())
        self.assertListEqual(response.data['usernames'], [])

    def test_get_status_with_user(self):
        access_tokens = self.create_users([username1, username2, username3])

        # user1 send friend request to user2, user3
        response = self.client.post(send_friend_request_url, {
            'username': username2
        }, headers={'Authorization': 'Bearer ' + access_tokens[0]})
        self.assertEqual(response.status_code, 201)
        response = self.client.post(send_friend_request_url, {
            'username': username3
        }, headers={'Authorization': 'Bearer ' + access_tokens[0]})
        self.assertEqual(response.status_code, 201)

        # user2 accept friend request from user1
        response = self.client.post(respond_to_friend_request_url, {
            'username': username1,
            'action': True
        }, headers={'Authorization': 'Bearer ' + access_tokens[1]})
        self.assertEqual(response.status_code, 202)

        # get status without authorization header
        response = self.client.get(get_status_with_user_url(username2))
        self.assertEqual(response.status_code, 401)

        # get status with user that does not exist
        response = self.client.get(get_status_with_user_url('username4'),
                                   headers={'Authorization': 'Bearer ' + access_tokens[0]})
        self.assertEqual(response.status_code, 404)

        # user1 get status with user2
        response = self.client.get(get_status_with_user_url(username2),
                                   headers={'Authorization': 'Bearer ' + access_tokens[0]})
        self.assertEqual(response.status_code, 200)
        self.assertIn('status', response.data.keys())
        self.assertEqual(response.data['status'], 'friends')

        # user2 get status with user1
        response = self.client.get(get_status_with_user_url(username1),
                                   headers={'Authorization': 'Bearer ' + access_tokens[1]})
        self.assertEqual(response.status_code, 200)
        self.assertIn('status', response.data.keys())
        self.assertEqual(response.data['status'], 'friends')

        # user2 get status with user3
        response = self.client.get(get_status_with_user_url(username3),
                                   headers={'Authorization': 'Bearer ' + access_tokens[1]})
        self.assertEqual(response.status_code, 200)
        self.assertIn('status', response.data.keys())
        self.assertEqual(response.data['status'], 'nothing')

        # user1 get status with user3
        response = self.client.get(get_status_with_user_url(username3),
                                   headers={'Authorization': 'Bearer ' + access_tokens[0]})
        self.assertEqual(response.status_code, 200)
        self.assertIn('status', response.data.keys())
        self.assertEqual(response.data['status'], 'outgoing_request_sent')

        # user3 get status with user1
        response = self.client.get(get_status_with_user_url(username1),
                                   headers={'Authorization': 'Bearer ' + access_tokens[2]})
        self.assertEqual(response.status_code, 200)
        self.assertIn('status', response.data.keys())
        self.assertEqual(response.data['status'], 'have_incoming_request')

        # user3 refuse friend request from user1
        response = self.client.post(respond_to_friend_request_url, {
            'username': username1,
            'action': False
        }, headers={'Authorization': 'Bearer ' + access_tokens[2]})
        self.assertEqual(response.status_code, 200)

        # user1 get status with user3
        response = self.client.get(get_status_with_user_url(username3),
                                   headers={'Authorization': 'Bearer ' + access_tokens[0]})
        self.assertEqual(response.status_code, 200)
        self.assertIn('status', response.data.keys())
        self.assertEqual(response.data['status'], 'nothing')

        # user3 get status with user1
        response = self.client.get(get_status_with_user_url(username1),
                                   headers={'Authorization': 'Bearer ' + access_tokens[2]})
        self.assertEqual(response.status_code, 200)
        self.assertIn('status', response.data.keys())
        self.assertEqual(response.data['status'], 'nothing')

    def test_remove_friend(self):
        access_tokens = self.create_users([username1, username2])

        # user1 send friend request to user2
        response = self.client.post(send_friend_request_url, {
            'username': username2
        }, headers={'Authorization': 'Bearer ' + access_tokens[0]})
        self.assertEqual(response.status_code, 201)

        # user2 send friend request to user1, accept automatically
        response = self.client.post(send_friend_request_url, {
            'username': username1
        }, headers={'Authorization': 'Bearer ' + access_tokens[1]})
        self.assertEqual(response.status_code, 202)

        # remove user1 from friends list without authorization header
        response = self.client.post(remove_friend_url, {
            'username': username1
        })
        self.assertEqual(response.status_code, 401)

        # invalid data
        response = self.client.post(remove_friend_url, {
            'username_': 'user1'
        }, headers={'Authorization': 'Bearer ' + access_tokens[1]})
        self.assertEqual(response.status_code, 400)

        # user1 remove from friends list user that does not exist
        response = self.client.post(remove_friend_url, {
            'username': 'user4'
        }, headers={'Authorization': 'Bearer ' + access_tokens[1]})
        self.assertEqual(response.status_code, 404)

        # user1 remove user2 from friends list
        response = self.client.post(remove_friend_url, {
            'username': username2
        }, headers={'Authorization': 'Bearer ' + access_tokens[0]})
        self.assertEqual(response.status_code, 202)

        # user1 remove user2 from friends list (user2 is not in friend list already)
        response = self.client.post(remove_friend_url, {
            'username': username2
        }, headers={'Authorization': 'Bearer ' + access_tokens[0]})
        self.assertEqual(response.status_code, 200)

    def create_users(self, usernames: list[str]) -> list[str]:
        access_tokens = []
        for username in usernames:
            response = self.client.post(create_user_url, {
                'username': username,
                'password': password
            })
            access_tokens.append(response.data['access'])
        return access_tokens
