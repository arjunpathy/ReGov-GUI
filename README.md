# ReGov-GUI
This repository contains the code for the GUI of ReGov Framework. You can find a detailed description of the ReGov Framework at this  [link](https://arxiv.org/pdf/2301.06919.pdf).

## Installation & Configuration
In order to run the application, the following depedencies are expected to beinstalled in the system, 
- [Truffle] v5.9.4
- [Ganache] v7.8.0
- [Node] v18.12.1
- [Python] 3.8.8
- [pip] 23.3.1 

Make sure the path environment variable is pointing to Python 3.8. For Windows 10,11: First copy the path where Python 3.8 is installed. A typical installation would have the following path,
```
C:\Users\MyUserName\AppData\Local\Programs\Python\Python38\Scripts
```
Then in Windows search, type `Environment Variable` and click on the `Edit the system environment variables` option. In the pop-up window click the `Environment Variable` button, and then select Path variable and click Edit. In the new pop-up window click on New and paste the copied path to the location where Python 3.8 is installed in your system.

[Download](https://github.com/arjunpathy/ReGov-GUI.git) and unzip the `ReGov-GUI.zip`. Then open the terminal and traverse the current directory to the project folder using the cd command.
```
For example: cd Downloads/ReGov-GUI
```

After reaching the ReGov-GUI folder in the terminal, install all Python dependencies by running
```
pip install -r requirements.txt
```

Compile and deploy all the smart contracts by running
```
truffle migrate or truffle migrate —reset
```

Open the file `DTaddresses.py` from `ReGov-GUI/node/PodManager/DTaddresses.py` and do the following

- Replace the `DTMONITORING` and `DTINDEXING` values with the new DTmonitoringOracle and DTindexing contract addresses ( logged in the terminal ) respectively.
- Make sure the value of `WEBPROVIDER` is the same as your ganache’s RPC server.
- Replace the value of `DEFAULT_POD_LOCATION` with your preferred location where you would like to create pods. The final folder must be named only as `Pod`.
```
For example: C:/Users/user1/Pod/ or D:/downloads/project/folder/Pod/
```

Create a folder named Pod in the same location mentioned above.

In the File, `DTaddress_generator.py` from `ReGov-GUI/node/PodManager/DTaddress_generator.py` in generate_account(), return the public and private keys of the first Eth account in Ganache. Click the Key icon to get the credentials.

To launch the app, ececute the command:
```
Python app.py
```



[//]: # 
[Truffle]: <https://trufflesuite.com/docs/truffle/how-to/install/>
[Ganache]: <https://trufflesuite.com/ganache/>
[Node]: <https://nodejs.org/en/download>
[Python]: <https://www.python.org/downloads/>
[pip]: <https://pip.pypa.io/en/stable/cli/pip_install/>