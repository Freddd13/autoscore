# Onedrive API
## Create app and get necessary data
Login to your Microsoft Azure account and go to the portal
Go to service "Azure Active Directory"
Go to App registration -> Register an application
    Give it a name
    Select the option with "... and personal Microsoft accounts (e.g. Skype, Xbox)"
     Set Redirect URI to some port on local host (Choose web application type), for instance http://localhost:9001
Go to API permissions and click "Add a permission"
    Add Microsoft Graph, then "Delegated Permissions"
    Add these permissions: profile, Files.ReadWrite, offline_access
Go to "Certificates & secrets" -> "New client secret"
    Store the value of the secret in environment variable AZURE_CLIENT_SECRET

## Login
```python
import onedrive.OnedriveManager

client_id = # app--> overview --> app(client) id
client_secret = # value when creating a secret
redirect_uri = 'http://localhost:9001'

om = OnedriveManager(client_id, client_secret, redirect_uri)
print(om.try_refresh_token())   # true --> OK, and token will be saved locally for future use.
```

## Using onedrive api
This is just a wrapper of auth of the python packge `microsoftgraph-python`. Check its docs for more:
> https://github.com/GearPlug/microsoftgraph-python
Note: the client in its docs acts as a public member in Class OnedriveManager Here, for example we call it here using:
```python
response = om.client.files.drive_update_existing_file(item_id, "/mnt/c/Users/i/Downloads/image2.jpg")
```

For it seems not to support large file upload, I patched a simple function directly in OnedriveManager, call it using:
```python
om.upload_large_file(r'C:\Users\Fred\Desktop\ustc-zheng-cn.zip', 'ustc-zheng-cn.zip')
```

It's recommand to first `try_refresh_token` everytime before calling API.


