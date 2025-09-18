# wlc-9800-ap-reboot
Gradually restart all AP connected to the WLC-9800 controller.

**Still in WIP but is working**

# How it works
Take X% (that you choose when executing the script) APs to reboot multiple time until there is no APs left.
It waits 80% of that X% APs to be UP before continuing. 

# Exemple
1500 AP to reboot 

-> choose 5%
75 AP will be reboot at the same time

The script is going to wait that **at least** 60 APs is UP before reboot the next 75 APs.
