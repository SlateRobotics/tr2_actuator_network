echo "Undoing autostart config"
sudo rm /etc/xdg/lxsession/LXDE-pi/autostart
sudo mv /etc/xdg/lxsession/LXDE-pi/autostart.bak /etc/xdg/lxsession/LXDE-pi/autostart

echo "Undoing eth0 interface config"
sudo rm /etc/dhcpcd.conf
sudo mv /etc/dhcpcd.conf.bak /etc/dhcpcd.conf

echo "Undoing hostapd config"
sudo rm /etc/hostapd/hostapd.conf
sudo mv /etc/hostapd/hostapd.conf.bak /etc/hostapd/hostapd.conf

echo "Uninstall complete. Please reboot."
