# Auto Halcyon
[HalyconMusic(ハルシオン Anime Piano Covers)](https://www.youtube.com/@HalcyonMusic) is an exceptionally talented piano content creator. Not only does he produce high-quality videos, but he also generously shares his sheet music for free for a limited time after his videos' release. To prevent missing out on the free sheet music due to a busy personal life, I created this repo. However, whenever I have time, I make sure to support the channel by liking, giving coins(bilibili), favoriting and leaving a comment. So even if using the flow, let's not just be passive viewers.

## Method
Periodically check his new video and run. Specifically:
Use RSS to get channel's latest video data, parse its sheet links and auto download them. 
Finally we send files via email or upload to onedrive(TODO).
The sensitive data is saved in Github repo's secrets thus it's safe.

**COMING SOON:**
- Q: So why to choose a more complicated way via youtube instead of fetching directly on the sheet website?

A: The repo will be refactored soon. Now I think it's ok to directly fetch via graphql WITHOUT RSS for that the sheet id seems to be increased by time. Once I use youtube rss because there's a timestamp in it and can be easily updated to the github repo.
Besides, I have made a pr to rsshub which directly returning freesheets data of any mymusicsheet user, which can simplify the code, lol.
- support any user

## Usage

### Use Github Action
1. Fork the repo
2. Use your own information to set the needed secrets in your repo(Repo Settings -- Secrets and variables -- Actions -- Secrets). You need an email with SMTP host, port, account and app password. Check out [User config](#(User-config)) for the full config we need.
![](docs/add_secrets.png)
3. Enable Workflow r/w permissions
Settings -- Actions -- General
![](docs/enable_rw.png)

Then the action will be triggered when pushing to repo or reaching a certain time everyday. The latter can be set in the auto_download.yml. 

### Use Docker
1. Download the config file:
```
wget https://github.com/Freddd13/auto-Halcyon/blob/main/localconfig.yaml?raw=true -O .localconfig.yaml
```
2. Replace your own data in the yaml above. Check out [User config](#(User-config)) for the full config we need.
3. Enable Workflow r/w permissions
3. Download image and run:
```
docker pull fredyu13/auto-halcyon
docker run -d --name auto-halcyon -v $(pwd)/.localconfig.yaml:/app/.localconfig.yaml fredyu13/auto-halcyon
```

### User config
| Variable                  | Description                                         | Example Value          |
|---------------------------|-----------------------------------------------------|------------------------|
| `MMS_email`               | Email associated with MMS website.                | `user@example.com`     |
| `MMS_password`            | Password for the MMS.                        | `passwordiiyokoiyo`          |
| `MMS_savefolder_path`     | Path to the save folder for MMS.                   | `files` (recommended)      |
| `RSS_url`                 | URL of the RSS feed.                               | `https://rsshub.app/youtube/user/@HalcyonMusic`|
| `RSS_max_days_difference` | Maximum allowable day difference for RSS entries.  | `14`  (recommended)                    |
| `RSS_max_trial_num`       | Maximum number of video posts attempt to download.     | `10` (recommended)                    |
| `enable_email_notify`      | Whether to notify downloading result via email  (1 enable, 0 disable)  | `1` |
| `Email_sender`            | Email address used to send emails.                 | `sender@example.com`   |
| `Email_receivers`         | Email addresses designated to receive emails.      | `receiver@example.com` |
| `Email_smtp_host`         | SMTP server address used to send emails.           | `smtp.example.com`     |
| `Email_smtp_port`         | SMTP server port used to send emails.              | `11451`                  |
| `Email_mail_license`      | SMTP password or authorization used for sending emails.  | `1145141919810`  |


## Develop
### Run locally
1. Clone this repo
2. Create a .localconfig.yaml from localconfig.yaml and fill in your data. Check out [User config](#(User-config)) for the full config we need.
3. `pip install -r requirements.txt`
4. Set env `AUTO_HALCYON_ENV` to `LOCAL`
4. `python main.py`

### Build Docker
1. Clone this repo
2. Create a .localconfig.yaml from localconfig.yaml and fill in your data. 
3. `docker build -t auto-halcyon -f docker/Dockerfile .`
4. `docker run -d --name auto_halcyon auto-halcyon:latest`
The schedule task can be adjusted by modifing the ./docker/crontab.

## Note
### About RSS
Currently the repo depends on [Youtube user route rss from RSSHub](https://docs.rsshub.app/routes/social-media#youtube-user). The url should be something like `https://rsshub.app/youtube/user/@HalcyonMusic`. The domain is strongly recommended to replaced with yours, because the public hub can be banned by source sites sometimes. And self-hosting one is quite benefit for your other future usage.
For more info, please check [RSSHub doc](https://docs.rsshub.app/).


### About Email
The `enable_email_notify` is used to send you downloading result including sheets and app log. If you disable the email, there's still another way to save your sheets: remove the `MMS_savefolder_path` directory if it exists in the `.gitignore`. The action will update the downloaded sheets to your repo. But it's not a good behavior to share others' sheets without permission, thus it's not recommended to disable email before other uploading method is supported.


## TODO
- [x] Email notification
- [x] Ignore History downloaded sheets
- [x] Docker support
- [ ] Save to Onedrive/Cloudreve


# Disclaimer:
The scripts provided in this repo is intended for personal use and convenience. It is the user's responsibility to use this tool in accordance with the terms of service and policies of MMS.

The author of this repo shall not be held responsible for any misuse or improper use of this tool, including but not limited to any violations of MMS's terms of service, copyright infringement, or any other legal or ethical concerns.

Users are advised to exercise discretion and adhere to all applicable laws and regulations when using this tool. The author of this tool disclaim all liability for any consequences resulting from the use of this tool.

By using this tool, you agree to accept all responsibility and legal consequences that may arise from its use.
Please use this tool responsibly and in compliance with MMS's terms and conditions.
