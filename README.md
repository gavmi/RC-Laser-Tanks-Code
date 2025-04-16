# Info
This repository contains Group 10, RC Laser Tanks, final code at the time of presenting this project. This code was created using python on a raspberry pi 4 model b and is used to run a game in which the players use an xbox controller connected to the pi via bluetooth to control the tanks. The tanks work by using IR LEDs and IR sensors on the tanks for firing while using two rear wheels controlled by motors and two front caster wheels. The motors are controlled using L298N motor drivers powered by an external 12 V battery.

Thank you to github user Berardinux for his Blackbriar repository and youtube videos that taugh us how to use an xbox controller to control our tanks. His repo can be found here: https://github.com/Berardinux/Blackbriar

# Connect Xbox Controller to bluetooth
bluetoothctl

scan on

pair XX:XX:XX:XX:XX:XX

trust XX:XX:XX:XX:XX:XX

connect XX:XX:XX:XX:XX:XX

# Look at Controller raw output
sudo evtest /dev/input/event0

# udev rules
sudo nano /etc/udev/rules.d/99-Blackbriar.rules {

SUBSYSTEM=="input", KERNELS=="event0", ACTION=="add", RUN+="/bin/systemctl start Blackbriar.service"

}

sudo udevadm control --reload-rules


# Systemd
sudo nano /etc/systemd/system/Blackbriar.service {

[Unit]
Description=Blackbriar Monitor Service
After=udev.service

[Service]
Type=simple
ExecStart=/home/berardinux/Documents/Blackbriar/Blackbriar.sh

[Install]
WantedBy=multi-user.target

}

sudo systemctl daemon-reload

sudo systemctl status blackbriar-monitor.service
