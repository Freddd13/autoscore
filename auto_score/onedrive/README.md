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
Use ms_auth.py to auth (get_access_token)

## Using Onedrive API
This is just a patch of the python packge `microsoftgraph-python`. Check its docs for more:
> https://github.com/GearPlug/microsoftgraph-python
Note: Here we just add a large-file-upload method, the microsoft grpah `access_token` from `ms_auth.py` or somewhere is needed to call this method.

For it seems that microsoftgraph-python does not support large file upload, I patched a simple function directly in OnedriveManager, call it using:
```python
upload_large_file(access_token, r'C:\Users\Fred\Desktop\ustc-zheng-cn.zip', 'ustc-zheng-cn.zip')
```


