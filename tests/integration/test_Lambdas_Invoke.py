import json
from time import sleep

from pbx_gs_python_utils.utils.Misc     import Misc

from osbot_aws.apis.Logs                import Logs

from osbot_aws.helpers.IAM_Policy       import IAM_Policy
from osbot_aws.helpers.Lambda_Package   import Lambda_Package
from osbot_aws.apis.IAM                 import IAM
from osbot_aws.apis.Lambda              import Lambda
from unittest                           import TestCase


# these tests require lambdas to already exist in AWS
class test_Lambdas_Invoke(TestCase):

    def test_dev_hello_world(self):
        assert Lambda('dev_hello_world').invoke() == 'hello None'

    def test_lambdas_gsbot_gsbot_graph(self):
        assert Lambda('lambdas_gsbot_gsbot_graph').invoke_raw().get('status') == 'ok'


    def test_lambda_write_cloud_watch(self):
        group_name      = '/unit-tests/test_log_group'
        stream_name     = Misc.random_string_and_numbers(prefix='tmp_stream_')
        message         = 'this is a message sent from an lambda function'
        lambda_name     = 'osbot_aws.lambdas.dev.write_cloud_watch_log'
        log_group_arn   = 'arn:aws:logs:eu-west-2:244560807427:log-group:{0}*'.format(group_name)
        policy_name     = 'temp_policy_for_lambda_write_cloud_watch'
        role_name       = 'temp_role_for_lambda_invocation'
        policy_actions  = ['logs:PutLogEvents']

        logs = Logs(group_name= group_name,stream_name=stream_name)
        logs.group_create()
        logs.stream_create()

        iam_role        = IAM(role_name=role_name)
        iam_policy      = IAM_Policy(policy_name=policy_name)
        iam_policy.add_statement_allow(policy_actions,[log_group_arn])

        policy_arn = iam_policy.create(delete_before_create=True).get('policy_arn')

        assert iam_policy.exists()           is True
        assert iam_role.role_exists()        is True
        assert logs.group_exists()           is True
        assert logs.stream_exists()          is True
        assert set(iam_role.role_policies()) == {'AWSXrayWriteOnlyAccess'                    ,
                                                 'policy_temp_role_for_lambda_invocation'    }

        iam_role.role_policy_attach(policy_arn)

        assert set(iam_role.role_policies()) == { 'AWSXrayWriteOnlyAccess'                   ,
                                                  'policy_temp_role_for_lambda_invocation'   ,
                                                  'temp_policy_for_lambda_write_cloud_watch' }

        sleep(10)                                        # wait for AWS to propagate role update
        payload = { 'group_name' : group_name  ,
                    'stream_name': stream_name ,
                    'message'    : message     }
        lambda_obj = Lambda_Package(lambda_name)        .update_with_root_folder()
        result     = lambda_obj.invoke(payload)
        from pbx_gs_python_utils.utils.Dev import Dev
        Dev.pprint(result)
        
        sleep(1)                                        # wait for Cloudwatch to update
        assert result.get('status') == 'ok'
        assert logs.messages() == [message]

        assert iam_policy.delete()           is True
        assert logs.group_delete()           is True
        assert logs.group_exists()           is False
        assert set(iam_role.role_policies()) == {'AWSXrayWriteOnlyAccess'                    ,
                                                'policy_temp_role_for_lambda_invocation'    }




        #Dev.pprint(result)

    # An error occurred (AccessDeniedException) when calling the '
    #               'DescribeLogStreams operation: User: '
    #               'arn:aws:sts::244560807427:assumed-role/temp_role_for_lambda_invocation/osbot_aws_lambdas_dev_write_cloud_watch_log '
    #               'is not authorized to perform: logs:DescribeLogStreams on '
    #               'resource: '
    #               'arn:aws:logs:eu-west-2:244560807427:log-group:/unit-tests/test_log_group:log-stream:',

    # @unittest.skip
    # def test_run_lambdas_in_multiple_accounts(self):
    #     Globals.aws_session_profile_name = 'gs-detect-aws'
    #     Globals.lambda_s3_bucket         = 'gs-detect-lambda'
    #     with Temp_Lambda() as _:
    #         _.invoke_raw().get('status') == 'ok'
    #
    #     Globals.aws_session_profile_name = 'default'












































