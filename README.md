# Auto Halcyon
HalyconMusic(ハルシオン Anime Piano Covers) is an exceptionally talented piano content creator. Not only does he produce high-quality videos, but he also generously shares his sheet music for free for a limited time after his videos' release. To prevent missing out on the free sheet music due to a busy personal life, I created this repo. However, whenever I have time, I make sure to support the channel by liking, giving coins(bilibili), favoriting and leaving a comment. So even if using the flow, let's not just be passive viewers.

## Method
Use Github Action to periodically check and run.
Use RSS to get channel's latest video data, parse its sheet links and auto download them. 
Finally we send files via email or upload to onedrive(TODO).
The sensitive data is saved in Github repo's secrets thus it's safe.

## Usage
1. Fork the repo
2. Use your own information to set the needed secrets in your repo. You need an email with SMTP host, port, account and app password.
Which secret need to set can be found in the .github/workflow/*.yml --> env:
3. Generate a personal Github access token in the Github settings - developer settings, and give the permission of reading && writing the repo VARIABLES to the token. Set this token as the value of PERSONAL_TOKEN in the repo secrets. 
4. Enable the action in the forked repos' ACTION by clicking the green button with "I understand XXX" (Well, I guess... lazy to test)

Then the action will be triggered when pushing to repo or reaching a certain time everyday. The latter can be set in the auto_download.yml. To develop locally, create a .localconfig.yaml from localconfig.yaml and replace in your data. 

## TODO
- [x] Email notification
- [x] Ignore History downloaded sheets
- [ ] Save to Onedrive
- [ ] Docker support


# Disclaimer:
The scripts provided in this repo is intended for personal use and convenience. It is the user's responsibility to use this tool in accordance with the terms of service and policies of MMS.

The author of this repo shall not be held responsible for any misuse or improper use of this tool, including but not limited to any violations of MMS's terms of service, copyright infringement, or any other legal or ethical concerns.

Users are advised to exercise discretion and adhere to all applicable laws and regulations when using this tool. The author of this tool disclaim all liability for any consequences resulting from the use of this tool.

By using this tool, you agree to accept all responsibility and legal consequences that may arise from its use.
Please use this tool responsibly and in compliance with MMS's terms and conditions.
