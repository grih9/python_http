class Settings:
    admins = ["admin", "root"]
    auth_resources = ["/private", "/secret"]
    auth_resources_methods = ["GET"]
    admin_resources = ["/admin", "/super_secret"]
    admin_resources_methods = ["GET"]
    no_auth_resources_methods = ["GET", "POST"]
    # login_resources = ["/login", "/relogin", "/auth"]
    login_resources = ["/check_login"]
    # admin_login_resources = ["/login/admin", "/relogin/admin", "/auth/admin"]

    need_auth = auth_resources + admin_resources
    need_auth_methods = ["GET"]
