# Auto Bridge T3RN

## Linux & VPS
```
sudo apt update && sudo apt upgrade
```
```
sudo apt-get install screen
```
```
ufw allow ssh
```
```
ufw enable
```
```
sudo apt-get install python3 python3-pip
```
```
sudo apt-get install git
```
```
git clone https://github.com/zamzasalim/tbot.git
```
```
cd tbot
```
```
python3 -m pip install -r requirements.txt
```
**Submit your Private Keys Metamask**
```
nano privateKeys.py
```
**Kemudian save `CTRL+XY dan Enter`**
### Run Bot
```
screen -S tbot
```
```
python3 run.py
```
**Kalo dah jalan langsung CTRL+AD**

## Termux & WIndows
```
pkg upgrade && pkg update
```
```
termux-setup-storage
```
```
pkg install python
```
```
pkg install git
```
```
git clone https://github.com/zamzasalim/tbot.git
```
```
cd tbot
```
```
pip install -r requirements.txt
```
**Submit your Private Keys Metamask**
```
nano privateKeys.py
```
**Kemudian save `CTRL+XY dan Enter`**
### Run bot
```
python run.py
```
## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
