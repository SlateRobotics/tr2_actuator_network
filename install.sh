echo "Editing autostart"
sudo cp -n /etc/xdg/lxsession/LXDE-pi/autostart /etc/xdg/lxsession/LXDE-pi/autostart.bak
sudo rm /etc/xdg/lxsession/LXDE-pi/autostart
sudo cp install/autostart /etc/xdg/lxsession/LXDE-pi/autostart
sudo chmod -R 777 /etc/xdg/lxsession/LXDE-pi/autostart

echo "Editing eth0 interface"
sudo cp -n /etc/dhcpcd.conf /etc/dhcpcd.conf.bak
sudo rm /etc/dhcpcd.conf
sudo cp install/dhcpcd.conf /etc/dhcpcd.conf
sudo chmod -R 777 /etc/dhcpcd.conf

echo "Editing hostapd"
sudo apt-get install hostapd -y
sudo cp -n /etc/hostapd/hostapd.conf /etc/hostapd/hostapd.conf.bak
sudo rm /etc/hostapd/hostapd.conf
sudo cp install/hostapd.conf /etc/hostapd/hostapd.conf
sudo chmod -R 777 /etc/hostapd/hostapd.conf

echo "Install complete. Please reboot"
