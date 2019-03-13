from flask_restful import Api
import miniverse.service.rest.v1 as v1

API_PREFIX = "miniverse"


def get_version(version_module):
    name = version_module.__name__
    return name.split(".")[-1]


def gen_resource_url(api_prefix, version_module, resource_name):
    url_parts = [api_prefix, get_version(version_module),
                 resource_name[1:] # skip first "/"
                 ]
    return "/"+"/".join(url_parts)


def setup_rest_api(flask_app):
    api = Api(flask_app)
    version = v1

    api.add_resource(version.User,
                     gen_resource_url(API_PREFIX, version, "/user/<user_id>"),
                     gen_resource_url(API_PREFIX, version, "/user"))

    # api.add_resource(version.UserBalance,
    #                  gen_resource_url(API_PREFIX, version, "/user/<user_id>/balance"))
    #
    # api.add_resource(version.Movement,
    #                  gen_resource_url(API_PREFIX, version, "/movement/<movement_id>"),
    #                  gen_resource_url(API_PREFIX, version, "/movement"))
    #
    # api.add_resource(version.Transfer,
    #                  gen_resource_url(API_PREFIX, version, "/transfer/<transfer_id>"),
    #                  gen_resource_url(API_PREFIX, version, "/transfer"))
