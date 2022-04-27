# Exploring Multipath TCP

## Installation

### Mininet Install

To install natively from source, first you need to get the source code:

```
git clone https://github.com/mininet/mininet
```

Note that the above git command will check out the latest and greatest Mininet (which we recommend!) If you want to run the last tagged/released version of Mininet - or any other version - you may check that version out explicitly:

```
cd mininet
git tag  # list available versions
git checkout -b mininet-2.3.0 2.3.0  # or whatever version you wish to install
cd ..
```
Once you have the source tree, the command to install Mininet is:

```
mininet/util/install.sh [options]
```
Typical install.sh options include:

-a: install everything that is included in the Mininet VM, including dependencies like Open vSwitch as well the additions like the OpenFlow wireshark dissector and POX. By default these tools will be built in directories created in your home directory.
-nfv: install Mininet, the OpenFlow reference switch, and Open vSwitch
-s mydir: use this option before other options to place source/build trees in a specified directory rather than in your home directory.
So, you will probably wish to use one (and only one) of the following commands:

To install everything (using your home directory): install.sh -a
To install everything (using another directory for build): install.sh -s mydir -a
To install Mininet + user switch + OvS (using your home dir): install.sh -nfv
To install Mininet + user switch + OvS (using another dir:) install.sh -s mydir -nfv
You can find out about other useful options (e.g. installing the OpenFlow wireshark dissector, if it’s not already included in your version of wireshark) using

```
install.sh -h
```

After the installation has completed, test the basic Mininet functionality:

```
sudo mn --switch ovsbr --test pingall
```

### MPTCP Kernel Install

```
# apt-key adv --keyserver hkp://keys.gnupg.net --recv-keys 379CE192D401AB61
# echo 'deb http://dl.bintray.com/cpaasch/deb jessie main' >> /etc/apt/sources.list
# apt-get update
# apt-get install linux-mptcp   # select "install package mantainer" if asked
```
#### Edit GRUB
```
# nano /etc/default/grub
```
And edit following lines:  
```
GRUB_DEFAULT=saved
GRUB_SAVEDEFAULT=true
GRUB_DISABLE_SUBMENU=y
```

```
# nano /etc/default/grub.d/50-cloudimg-settings.cfg
```
And comment following line, if present  
```
#GRUB_DEFAULT=0
```

#### Show all installed kernels
```
# export GRUB_CONFIG=`find /boot -name "grub.cfg"`
# update-grub
# grep 'menuentry ' $GRUB_CONFIG | cut -f 2 -d "'" | nl -v 0
```

#### Test kernel
Choose the MPTCP kernel from the list and set it as kernel for next boot only  
```
# grub-reboot 'Ubuntu, with Linux 4.9.60.mptcp'
# reboot
```
So, if something went wrong, you can reboot again from control panel, and the default kernel will be used

#### Show actual kernel
Check if you the running kernel is MPTCP
```
# uname -ir
```

#### Change kernel
Set the MPTCP kernel as default
```
# grub-set-default 'Ubuntu, with Linux 4.9.60.mptcp'
# reboot
```
