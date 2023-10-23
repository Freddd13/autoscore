class GithubAPI:
    def __init__(self, token, owner_repo):
        # self.token = token
        self.headers = {
            'Accept': 'application/vnd.github+json',
            'Authorization': f'Bearer {token}',
            'X-GitHub-Api-Version': '2022-11-28',
        }
        self.owner_repo = owner_repo


    def create_variables(self, name, value) -> bool:
        data = {
            'name': name,
            'value': value
        }
        url = f'https://api.github.com/repos/{self.owner_repo}/actions/variables'
        response = requests.post(url, headers=self.headers, json=data)
        # logger.debug(response.text)
        return response.status_code==201


    def update_variables(self, name, value) -> bool:
        try:
            data = {
                'name': name,
                'value': value
            }
            url = f'https://api.github.com/repos/{self.owner_repo}/actions/variables/{name}'
            response = requests.patch(url, headers=self.headers, json=data)
            logger.debug(response.text)
        except Exception as e:
            logger.error(str(e))
        return response.status_code==204

