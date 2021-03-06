## Holds permission data for a private race room

def get_permission_info(server, race_private_info):
    permission_info = PermissionInfo()
    for admin_name in race_private_info.admin_names:
        for role in server.roles:
            if role.name.lower() == admin_name.lower():
                permission_info.admin_roles.append(role)
        for member in server.members:
            if member.name.lower() == admin_name.lower():
                permission_info.admins.append(member)

    for racer_name in race_private_info.racer_names:
        for member in server.members:
            if member.name.lower() == racer_name.lower():
                permission_info.racers.append(member)

    return permission_info
        
class PermissionInfo(object):

    def __init__(self):
        self.admins = []
        self.admin_roles = []
        self.racers = []

    def is_admin(self, member):
        for role in member.roles:
            if role in self.admin_roles:
                return True
        if member in self.admins:
            return True

        return False
