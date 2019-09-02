echo "Updating system"
sudo apt-get update
sudo apt-get dist-upgrade -y
sudo apt-get install hostapd dnsmasq -y

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
sudo cp -n /etc/hostapd/hostapd.conf /etc/hostapd/hostapd.conf.bak
sudo rm /etc/hostapd/hostapd.conf
sudo cp install/hostapd.conf /etc/hostapd/hostapd.conf
sudo chmod -R 777 /etc/hostapd/hostapd.conf

echo "Editing dnsmasq"
sudo cp -n /etc/dnsmasq.conf /etc/dnsmasq.conf.bak
sudo rm /etc/dnsmasq.conf
sudo cp install/dnsmasq.conf /etc/dnsmasq.conf
sudo chmod -R 777 /etc/dnsmasq.conf

echo "Enable SSH -> \"Interfacing Options\" -> \"SSH\""
sudo raspi-config

echo "Install complete. Please reboot"
