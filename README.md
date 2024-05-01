# gve_devnet_meraki_policy_object_mx_rule_creation

## Contacts
* Trevor Maco

## Solution Components
* Meraki

## Related Sandbox Environment
This is as a template, project owner to update

This sample code can be tested using a Cisco dCloud demo instance that contains ** *Insert Required Sandbox Components Here* **



## Docker Image / GitHub Actions Deployment

To make the code more **portable** and **easier** for users to deploy, you can automatically create a GitHub Package (Docker Image) or GitHub Release (GoLang Application Binaries) by configuring the relevant files in `.github/workflows` and the repo. Users then have the option to pull and run the docker image (or binaries) with your application and environment configured to skip over setup steps (ex: installing python). 

Refer to the documentation [here](https://wwwin-github.cisco.com/gve/docker-and-github-actions-templates) for how to set up this functionality.


## Prerequisites
#### Meraki API Keys
In order to use the Meraki API, you need to enable the API for your organization first. After enabling API access, you can generate an API key. Follow these instructions to enable API access and generate an API key:
1. Login to the Meraki dashboard
2. In the left-hand menu, navigate to `Organization > Settings > Dashboard API access`
3. Click on `Enable access to the Cisco Meraki Dashboard API`
4. Go to `My Profile > API access`
5. Under API access, click on `Generate API key`
6. Save the API key in a safe place. The API key will only be shown once for security purposes, so it is very important to take note of the key then. In case you lose the key, then you have to revoke the key and a generate a new key. Moreover, there is a limit of only two API keys per profile.

> For more information on how to generate an API key, please click [here](https://developer.cisco.com/meraki/api-v1/#!authorization/authorization). 

> Note: You can add your account as Full Organization Admin to your organizations by following the instructions [here](https://documentation.meraki.com/General_Administration/Managing_Dashboard_Access/Managing_Dashboard_Administrators_and_Permissions).

#### Meraki Camera MQTT API
**MQTT Broker**: MQTT-based protocols use a publish-subscribe connection between the client and server. In the case of MV Sense, the server is continuously pushing messages to the MV smart cameras so the device can respond instantly. This leads to a real-time feed of data coming from your camera. Follow these steps to configure a MQTT broker:
1. Start by navigating to `Cameras > Monitor > Cameras` and selecting the camera you would like to enable MV Sense on.
2. Once the camera is selected, go to `Settings > Sense`.
3. Click `Enabled`.
4. To enable MQTT on your camera and create a new MQTT broker configuration click `Add or edit MQTT Brokers`.
 
> For more information on using MQTT with Meraki cameras, please click [here](https://developer.cisco.com/meraki/mv-sense/#!mqtt/configuring-mqtt-in-the-dashboard).

> Note: If this is your organization's first time using MV Sense, you will have 10 free perpetual licenses available to use. If you have exceeded this 10 free license count, you must activate more licenses by navigating to `Organization > Configure > License Info` and claim more licenses.

## Installation/Configuration
1. Clone this repository with `git clone [repository name]`. To find the repository name, click the green `Code` button above the repository files. Then, the dropdown menu will show the https domain name. Click the copy button to the right of the domain name to get the value to replace [repository name] placeholder.
![git-clone.png](git-clone.png)
2. Add Meraki API key to environment variables
```python
API_KEY = "API key goes here"
```
3. Set up a Python virtual environment. Make sure Python 3 is installed in your environment, and if not, you may download Python [here](https://www.python.org/downloads/). Once Python 3 is installed in your environment, you can activate the virtual environment with the instructions found [here](https://docs.python.org/3/tutorial/venv.html).
4. Install the requirements with `pip3 install -r requirements.txt`

## Usage
To run the program, use the command:
```
$ python3 program-name.py
```

# Screenshots

![/IMAGES/0image.png](/IMAGES/0image.png)

### LICENSE

Provided under Cisco Sample Code License, for details see [LICENSE](LICENSE.md)

### CODE_OF_CONDUCT

Our code of conduct is available [here](CODE_OF_CONDUCT.md)

### CONTRIBUTING

See our contributing guidelines [here](CONTRIBUTING.md)

#### DISCLAIMER:
<b>Please note:</b> This script is meant for demo purposes only. All tools/ scripts in this repo are released for use "AS IS" without any warranties of any kind, including, but not limited to their installation, use, or performance. Any use of these scripts and tools is at your own risk. There is no guarantee that they have been through thorough testing in a comparable environment and we are not responsible for any damage or data loss incurred with their use.
You are responsible for reviewing and testing any scripts you run thoroughly before use in any non-testing environment.