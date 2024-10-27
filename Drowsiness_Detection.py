from scipy.spatial import distance
from imutils import face_utils
import imutils
import dlib
import cv2
from playsound import playsound  # Import playsound for alarm sound

def eye_aspect_ratio(eye):
	A = distance.euclidean(eye[1], eye[5])
	B = distance.euclidean(eye[2], eye[4])
	C = distance.euclidean(eye[0], eye[3])
	ear = (A + B) / (2.0 * C)
	return ear

thresh = 0.25
frame_check = 25
detect = dlib.get_frontal_face_detector()
predict = dlib.shape_predictor("models/shape_predictor_68_face_landmarks.dat")  # Dat file is the crux of the code

(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_68_IDXS["left_eye"]
(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_68_IDXS["right_eye"]
cap = cv2.VideoCapture(0)
flag = 0
alarm_playing = False  # To avoid multiple alarm sounds

while True:
	ret, frame = cap.read()
	frame = imutils.resize(frame, width=450)
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	subjects = detect(gray, 0)
	for subject in subjects:
		shape = predict(gray, subject)
		shape = face_utils.shape_to_np(shape)  # converting to NumPy Array
		leftEye = shape[lStart:lEnd]
		rightEye = shape[rStart:rEnd]
		leftEAR = eye_aspect_ratio(leftEye)
		rightEAR = eye_aspect_ratio(rightEye)
		ear = (leftEAR + rightEAR) / 2.0
		leftEyeHull = cv2.convexHull(leftEye)
		rightEyeHull = cv2.convexHull(rightEye)
		cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
		cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)

		if ear < thresh:
			flag += 1
			print(flag)
			if flag >= frame_check:
				# Display the alert message
				cv2.putText(frame, "!!! DROWSINESS DETECTED !!!", (30, 30),
				            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 3)
				cv2.putText(frame, "PLEASE WAKE UP!", (50, 70),
				            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
				cv2.putText(frame, "WARNING! EYES CLOSING!", (10, 110),
				            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
				
				# Play the alarm sound
				if not alarm_playing:
					playsound('alarm.wav')  # Play the alarm sound
					alarm_playing = True  # Set flag to prevent multiple alarms
		else:
			flag = 0
			alarm_playing = False  # Reset the alarm flag

	cv2.imshow("Frame", frame)
	key = cv2.waitKey(1) & 0xFF
	if key == ord("q"):
		break

cv2.destroyAllWindows()
cap.release()
