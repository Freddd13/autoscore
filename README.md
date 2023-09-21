# Auto Halcyon
[HalyconMusic(ハルシオン Anime Piano Covers)](https://www.youtube.com/@HalcyonMusic) is an exceptionally talented piano content creator. Not only does he produce high-quality videos, but he also generously shares his sheet music for free for a limited time after his videos' release. To prevent missing out on the free sheet music due to a busy personal life, I created this repo. However, whenever I have time, I make sure to support the channel by liking, giving coins(bilibili), favoriting and leaving a comment. So even if using the flow, let's not just be passive viewers.

## Method
Periodically check his new video and run. Specifically:
Use RSS to get channel's latest video data, parse its sheet links and auto download them. 
Finally we send files via email or upload to onedrive(TODO).
The sensitive data is saved in Github repo's secrets thus it's safe.

Note: Currently we use [Youtube user route rss from RSSHub](https://docs.rsshub.app/routes/social-media#youtube-user). The url should be something like `https://rsshub.app/youtube/user/@HalcyonMusic`. The domain is strongly recommended to replaced with yours, because the public hub can be banned by source sites sometimes.
For more info, please check [RSSHub doc](https://docs.rsshub.app/).

## Usage
### Use Github Action
1. Fork the repo
2. Use your own information to set the needed secrets in your repo. You need an email with SMTP host, port, account and app password.
Which secret need to set can be found in the .github/workflow/*.yml --> env:
3. Generate a personal Github access token in the Github settings - developer settings, and give the permission of reading && writing the repo VARIABLES to the token. Set this token as the value of PERSONAL_TOKEN in the repo secrets. 
4. Enable the action in the forked repos' ACTION by clicking the green button with "I understand XXX" (Well, I guess... lazy to test)

Then the action will be triggered when pushing to repo or reaching a certain time everyday. The latter can be set in the auto_download.yml. 

### Use Docker
1. Clone this repo
2. Create a .localconfig.yaml from localconfig.yaml and fill in your data. 
3. `docker build -t auto-halcyon -f docker/Dockerfile .`
4. `docker run -d --name auto_halcyon auto-halcyon:latest`
The schedule task can be adjusted by modifing the ./docker/crontab.

### Develop locally
1. Clone this repo
2. Create a .localconfig.yaml from localconfig.yaml and fill in your data. 
3. `pip install -r requirements.txt`
4. Set env `AUTO_HALCYON_ENV` to `LOCAL`
4. `python main.py`

## TODO
- [x] Email notification
- [x] Ignore History downloaded sheets
- [x] Docker support
- [ ] Save to Onedrive


# Disclaimer:
The scripts provided in this repo is intended for personal use and convenience. It is the user's responsibility to use this tool in accordance with the terms of service and policies of MMS.

The author of this repo shall not be held responsible for any misuse or improper use of this tool, including but not limited to any violations of MMS's terms of service, copyright infringement, or any other legal or ethical concerns.

Users are advised to exercise discretion and adhere to all applicable laws and regulations when using this tool. The author of this tool disclaim all liability for any consequences resulting from the use of this tool.

By using this tool, you agree to accept all responsibility and legal consequences that may arise from its use.
Please use this tool responsibly and in compliance with MMS's terms and conditions.
