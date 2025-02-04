#!/usr/bin/env python

import rospy
from geometry_msgs.msg import PoseStamped
import sys
import usb.core
import usb.util
# decimal vendor and product values
dev = usb.core.find(idVendor=16700, idProduct=12314)                
#this id is found by using the finddevices code
# or, uncomment the next line to search instead by the hexidecimal equivalent
#dev = usb.core.find(idVendor=0x45e, idProduct=0x77d)
# first endpoint
interface = 0
endpoint = dev[0][(0,0)][0]
# if the OS kernel already claimed the device, which is most likely true
# thanks to http://stackoverflow.com/questions/8218683/pyusb-cannot-set-configuration
if dev.is_kernel_driver_active(interface) is True:
  # tell the kernel to detach
	dev.detach_kernel_driver(interface)
  # claim the device
	usb.util.claim_interface(dev, interface)
x=0.0
y=0.0
factor = 0.0218
publish = rospy.Publisher('odom', PoseStamped , queue_size = 10)
pose = PoseStamped()
rospy.init_node('blabbermouth', anonymous =True)
rate = rospy.Rate(10)
while not rospy.is_shutdown():
	try: 
		data = dev.read(endpoint.bEndpointAddress,endpoint.wMaxPacketSize)
		if data[1]<=127:      #IF the mouse is moving in the positive X direction, add dX
			x=x+data[1]*factor  
		else:
			x=x-(256-data[1])*factor   #else subtract dX
		if data[2]<=127:      #IF the mouse is moving in the positive Y direction, add dY
			y=y-data[2]*factor
		else:
			y=y+(256-data[2])*factor  #else subtract dY
		print(x," ",y)
	except usb.core.USBError as e:
		data = None
		if e.args == ('Operation timed out',):
			continue
	pose.header.stamp = rospy.Time.now()
	pose.pose.position.x = x
	pose.pose.position.y = y
	rospy.loginfo(pose)#	publish.publish(pose)
	rate.sleep()
    #time.sleep(0.01)
# release the device
usb.util.release_interface(dev, interface)
# reattach the device to the OS kernel
dev.attach_kernel_driver(interface)
