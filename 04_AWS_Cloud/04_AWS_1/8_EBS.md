# EBS
## Introduction

## Exercise
**Exercise 1:** 

Create a t2.micro Amazon Linux 2 machine with all the default settings.
Create a new EBS volume with the following requirements:
- Volume type: General Purpose SSD (gp3)
- Size: 1 GiB
- Availability Zone: same as your EC2

## Results
**Exercise 1:** I created a new instance and created a new EBS volume as well. 

![PrnScr](/00_includes/04_AWS1/9_EBS.png)

The instance is running and the new EBS volume is available. 

**Exercise 2:** I attached the EBS volume to my instance by using the `Attach volume` button that is under the Actions tab.
The volume state now changes from availabe to in-use.

![PrnScr](/00_includes/04_AWS1/10_EBS_SSHlogin.png)

After connecting to my instance, I want to list available block devices and identify my EBS volume, I do so by using the following command:

```
lsblk
```
I need to create a directory to serve as the mount point and mount the EBS volume, I do so by using the following two commands: 
``` 
sudo mkdir /opslag
sudo mount /dev/xvdf /opslag
```
After that I navigate to that directory so that I can create a text file.

I do so by:

```
cd /opslag
```

Now that I am in the correct directory I can create a text by using the nano editor:
```
sudo nano myfirstEBS.txt
```
In the nano editor I write my text: "This is my first text file on the mounted EBS volume!"

I confirm my text by using the following command:
``` 
cat /opslag/myfirstEBS.txt
```

![PrnScr](/00_includes/04_AWS1/11_Mounted_EBS.png)

**Exercise 3:** 
I made snapshot of the volume.

![PrnScr](/00_includes/04_AWS1/12_Snapshot.png)

![PrnScr](/00_includes/04_AWS1/13_New_volume.png)

## Sources
- https://www.youtube.com/watch?v=VJBtqORxNLU
