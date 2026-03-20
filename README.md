# AI-Powered-Gig-worker-Insurance

## Problem Statement
Gig workers (delivery partners) face income loss due to external disruptions like weather, pollution, and curfews. Currently, there is no protection mechanism for such unpredictable income drops. Our solution provides an AI-driven parametric insurance platform that automatically compensates workers for lost income.

## Target Persona
- Quick commerce delivery partner in platforms like Zepto, Blinkit, Swiggy etc in Bengaluru  

Example:  
- Name: Ravi  
- Role: Quick commerce Delivery Partner (Zomato/Swiggy)  
- Location: Bengaluru  
- Work Pattern: 10–12 hours/day  

### Pain Points
- Cannot work in heavy rain  
- Earnings drop during extreme weather  
- No financial safety net  

## Key Disruptions Covered
Since we have a persona of a quick commerce delivery partner, the key disruptions we mainly observe are:  
- Heavy Rain  
- Extreme Heat  
- Flooded Roads  
- Heavy Traffic  
- Curfews  

## Solution Overview
We propose an AI-powered parametric insurance system that:  
- Predicts disruption risks  
- Calculates weekly premiums dynamically  
- Automatically triggers claims  
- Provides instant payouts  

The system ensures minimal manual intervention and a seamless user experience.

## Must-Have Features

### 1. AI Powered Risk Assessment
We use a simple AI/ML-based approach to estimate risk and calculate weekly premiums dynamically. Instead of fixing a probability manually, we train a lightweight model (like logistic regression or a basic classifier) to predict the probability of a disruption event **P**.  

**Model Inputs:**  
- Weather forecast data (rain probability, temperature)  
- Historical disruption patterns in that area  
- Location risk score (e.g., flood-prone zones)  
- Seasonal trends (monsoon, summer, etc.)  

Each of these inputs acts as a feature, and the model learns how strongly each factor contributes to disruption risk. For example, high rainfall prediction + flood-prone area → higher probability.

**Expected Income Loss Calculation:**  

$$
EL = P \times (I_d \times D)
$$

Where:  
- $I_d$ = average daily income of the worker  
- $D$ = expected number of working days lost in a week  

**Weekly Premium Formula:**  

$$
Premium = EL \times (1 + \alpha + \beta)
$$

Where:  
- $\alpha$ = profit margin  
- $\beta$ = safety buffer for uncertainty  

As more users interact with the system, we collect real data (actual disruptions vs predicted ones). This data is used to retrain or fine-tune the model, so over time the predictions become more accurate and personalized for each worker and location.

### 2. Fraud Detection
For fraud detection, we combine rule-based checks with basic anomaly detection techniques to identify unusual or suspicious behavior.  

- First, we validate whether a disruption actually occurred by comparing the user’s GPS location with external data like weather APIs. If a user claims loss due to heavy rain but the weather data shows no such event in that area, the claim is flagged.  
- Next, we analyze movement patterns using GPS data. We calculate speed and distance between location updates — if unrealistic jumps are detected (e.g., traveling several kilometers in a few minutes), it indicates GPS spoofing or manipulation.  
- We apply anomaly detection on user behavior. Over time, we build a profile of normal behavior (average claims/week, typical working hours). Deviations such as excessive claims or claiming only during high payout conditions are flagged.  

These checks can be implemented using statistical thresholds or basic ML models (clustering/outlier detection). This helps automatically identify suspicious activity while keeping the claim process smooth for genuine users.

### 3. Parametric Automation
Our app uses a fully automated parametric pipeline to monitor external disruptions and worker activity, enabling automatic claim processing without manual filing.

- The system collects data from multiple sources: weather APIs (rainfall, alerts), AQI APIs (pollution levels), traffic data, worker GPS telemetry, and simulated platform earnings.  
- A background scheduler polls these sources at fixed intervals, normalizes the data, and generates a **disruption score** based on weighted factors like rainfall, pollution, traffic, and demand drop.  

**Disruption Event Trigger:**  

$$
disruption\_score = w_1 \times rainfall + w_2 \times aqi + w_3 \times traffic + w_4 \times demand\_drop
$$

When the score exceeds a threshold, a disruption event is created.

- **Geo-Spatial Validation:** GPS data is mapped to geofenced zones, and distance checks (Haversine formula) confirm workers are within the disruption radius.  
- **Automatic Claim Initiation:** Worker activity and earnings are compared against expected income predicted by an ML regression model. If actual earnings drop below threshold, a claim is generated automatically with details like user ID, event ID, and income loss.  
- **Instant Payout Processing:** Payments are triggered via a mock gateway (Razorpay test mode), and workers are notified instantly. The workflow—Claim Creation → Validation → Fraud Check → Approval → Payout—ensures fast, accurate, and seamless support.  

The pipeline is modular, event-driven, scalable, and employs multi-layer validation to minimize false triggers.

### 4. API Integration
- **OpenWeatherMap API:** Retrieve real-time weather data (rainfall, temperature, alerts) to identify environmental conditions affecting users.  
- **NewsAPI:** Provides live news for events like accidents or disasters to validate disruption occurrences.  
- **Google Maps API & Traffic APIs:** Gather traffic congestion and route condition data affecting deliveries.  
- **Firebase:** Stores user information, activity data, and system outputs in a cloud-based NoSQL database for real-time access.  
- **Razorpay:** Handles secure payment transactions and automated payouts.  
- **Twilio:** Sends notifications (SMS/alerts) to users regarding claims or system events.

## Workflow
1. User registers and selects insurance plan  
2. System collects location + activity data  
3. AI model predicts disruption probability  
4. Weekly premium is calculated dynamically  
5. External APIs monitor real-time disruptions  
6. If trigger condition is met → claim auto-initiated  
7. Payout processed instantly

## Tech Stack
- **Frontend (Mobile App for Gig Workers):**  
  - React Native – Cross-platform mobile development  
  - Expo – Simplifies testing, GPS access, push notifications  

- **Backend (API & Business Logic):**  
  - FastAPI (Python) – High-performance, async-ready  
  - Celery + Redis – Background tasks (trigger monitoring, periodic polling, claim automation)  

- **Database:**  
  - Firebase Firestore – Real-time NoSQL for user profiles, earnings, claims, geo-tagged events  
  - Firebase Realtime Database (optional) – For live GPS streams  

- **AI/ML:**  
  - Scikit-learn & PyTorch – Predictive modeling and anomaly detection  
  - Pickle – Serialize ML models for backend integration  

- **DevOps & Deployment:**  
  - Firebase Hosting – Backend & static assets  
  - GitHub – Version control  

## Weekly Pricing Model
- Based on predicted probability of disruption  
- Uses expected loss calculation  
- Includes profit margin + risk buffer  
- Dynamically adjusts per worker and location  

## Key Features
- AI-based risk prediction  
- Dynamic weekly premium  
- Automated claim triggering  
- Fraud detection system  
- Instant payout simulation  

## Future Enhancements
- Advanced ML models for better prediction  
- Real-time traffic integration  
- Personalized insurance plans  
- Multi-city scaling

Market Crisis:

# Adversarial Defense & Anti-Spoofing Strategy

## 1. Differentiation

Our system uses multi-factor verification to differentiate genuinely stranded delivery partners from GPS-spoofing bad actors:

- **Real-time location cross-validation** with multiple sensors (GPS + WiFi triangulation + cell tower data)
- **Correlation with local conditions**: weather, traffic, and operational platform data
- **Behavioral analytics** for normal activity patterns:
 - Shift start/end times
 - Average speed
 - Number of claims

## 2. Data Analysis

To detect coordinated fraud rings, we analyze:

- **Clustered claims** from multiple users in the same zones/timeframes
- **GPS anomaly patterns**:
 - Jumps
 - Impossible speed
 - Repeated coordinates
- **Temporal behavior**:
 - Claim frequency spikes vs. normal historical data
- **Device & app telemetry**:
 - Cross-referencing device identifiers
 - App usage patterns

## 3. UX Balance

To ensure honest users are not penalized:

- **Soft verification** for flagged claims, allowing conditional payout or temporary hold
- **Manual review option** for extreme edge cases
- **AI confidence scores** guide decision-making rather than blanket rejection
- **Transparent notifications** inform users if their claim is under review

This multi-layer strategy ensures **robust anti-spoofing protection** while maintaining **fairness and trust** for legitimate workers.

## GitHub Repo Link
[https://github.com/Adithya-P-Vishwamitra/GIGSURANCE.git](https://github.com/Adithya-P-Vishwamitra/GIGSURANCE.git)

## Team Members
1. Guruprasad N Gowda  
2. Adithya B  
3. Adithya P Vishwamitra
