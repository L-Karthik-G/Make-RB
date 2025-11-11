#  Make Roads Better (Make RB)

**Make Roads Better (Make RB)** is an Android-based pothole detection application that helps identify and report road potholes using real-time accelerometer and GPS data from your mobile device.  
The goal is to make roads safer by collecting and sharing data about poor road conditions with drivers and authorities.

---

##  Theory(Overview)

The app continuously analyzes changes in the **Z-axis acceleration** (the up–down movement of your phone) to detect potholes.  
When a sudden spike or drop is detected within a defined threshold, the app marks that as a potential pothole and records its **GPS location**.

This data is stored in a central database and used to display potholes along your **current route or destination**, helping users avoid rough road segments.

---

##  How It Works

1. Continuously monitors **accelerometer data** from the phone.  
2. Detects potholes based on sudden changes in vertical acceleration.  
3. Records the **GPS coordinates** of each detected pothole.  
4. Sends the information to a **central database**.  
5. Displays reported potholes along your route or destination in real time.

---

##  Installation Instructions For APK (Android Only)

You can install and start using **Make Roads Better (Make RB)** by following these steps:

1. **Download the APK**

    [Click here to download MAKE-RB_Prototype_1.apk] [MAKE-RB_Prototype_1.apk](https://github.com/L-Karthik-G/Make-RB/releases/download/v1.0/MAKE-RB_Prototype._1.apk)
   
    **Prototype 1 only detects potholes and updates them to a secure Firebase database. You can shake your phone to test the pothole detection.**
  

3. **Install the App**
   - Transfer the APK to your Android device (if downloaded on PC).  
   - On your phone, go to:  
     **Settings → Security → Install unknown apps → Allow for your file manager/browser**  
   - Open the APK file and tap **Install**.

4. **Run the App**
   - Open **Make Roads Better** from your app drawer.  
   - Allow access to **Location** and **Motion Sensors** when prompted.  
   - Start driving — the app will automatically detect potholes and mark them on the map.

---

## End Product 

**To create an app that**
- Updates real-time pothole detection using accelerometer data  
- Automatates GPS tagging of detected potholes  
- Displays potholes along your route  
- Centralizes pothole database for crowdsourced reporting  

---

##  Future Improvements

- Improve detection accuracy using **AI/ML-based motion analysis**  
- Add **offline support** for low-connectivity areas  
- Enable **community-driven pothole verification**  
- Provide **severity ratings** for detected potholes
- To integrate this whith a **computer vison model** which uses dashcam footage to detect undualated,potholed roads and update its location on to the app

---

##  Goal

To make roads safer and smoother by **crowdsourcing pothole data** from everyday drivers, enabling proactive action by communities and authorities.

