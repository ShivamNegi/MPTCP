if [ $# -eq 0 ]
then
    echo "Filename not supplied"
    exit 1
fi

sudo rm iperf*
sudo mn -c
sudo python $1
