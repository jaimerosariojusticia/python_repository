name = "credentials"

def ssh_local_id():
    USERID = 'iamgroot'
    return USERID

def ssh_local_keystring():
    KEYSTRING = '''
put here you id_rsa.pub base64 string only
'''
    return KEYSTRING

def ssh_local_keyhash():
    KEYHASH = 'put here your base64 hash only'
    return KEYHASH