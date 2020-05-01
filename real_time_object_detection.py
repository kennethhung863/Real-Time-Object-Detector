import cv2
import os, io
from google.cloud import vision

# object detection function
def object_detection(img):
    # initialize Google Cloud Console Project: replace Service_Account_Token.json with your .json file name
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'Service_Account_Token.json'
    client = vision.ImageAnnotatorClient()

    # opens image
    with io.open(img, 'rb') as image_file:
        content = image_file.read()

    # object detection
    image = vision.types.Image(content=content)
    objects = client.object_localization(image=image).localized_object_annotations

    return objects


def display_objects(objects, img):
    # getting dimensions to display boxes around objects
    size = cv2.imread(img).shape
    display_width = int(size[1])
    display_height = int(size[0])
    text_size = int(display_width/80)

    # displaying objects using rectangles with their confidence score
    for i in range(len(objects)):
        vertices = objects[i].bounding_poly.normalized_vertices
        x = int(vertices[0].x*display_width)
        y = int(vertices[0].y*display_height)
        str = ('{}: {}%'.format(objects[i].name, round(objects[i].score, 3)*100))
        text_length = cv2.getTextSize(str, font, 1, 1)

        # white background
        cv2.rectangle(frame,(x, int(y-(text_size/2)-text_length[0][1])), (x+text_length[0][0], y), (255, 255, 255), -1)
        # black text
        cv2.putText(frame, str, (x, int(y-(text_size/4))), font, 1, (0,0,0), 1)
        # actual box
        cv2.rectangle(frame, (x, y), (int(vertices[2].x*display_width), int(vertices[2].y*display_height)), (0, 255, 0), int(text_size/5))
 


# setting up video capture, resolution will be the largest that the default camera supports
vid = cv2.VideoCapture(0, cv2.CAP_DSHOW)
vid.set(cv2.CAP_PROP_FRAME_WIDTH, 10000)
vid.set(cv2.CAP_PROP_FRAME_HEIGHT, 10000)

# recognition initialization:
# by default, the start is the space bar, flip is f
flip = False
button_pressed = False
# counter to slow down object detection, since there is a limit from google vision
counter = 100
# initialize object with none so it is retained throughout the while loop
object = None
# font of object text
font = cv2.FONT_HERSHEY_PLAIN

# camera and object detection loop
while(True): 
    # start camera, capture frame
    ret, frame = vid.read() 
    # flip if f is pressed
    if flip:
        frame = cv2.flip(frame, 1)

    # display the frame and instructions
    cv2.rectangle(frame,(0,0), (175,50), (255, 255, 255), -1)
    cv2.putText(frame, 'Esc - Exit', (5,15), font, 1, (0,0,0), 1)
    cv2.putText(frame, 'Space - Start/Stop', (5,30), font, 1, (0,0,0), 1)
    cv2.putText(frame, 'F - Flip Image', (5,45), font, 1, (0,0,0), 1)

    # when the button is pressed, turn on object detection and update the detection every time counter hits set limit
    if button_pressed:

        # take a temporary picture, then use Vision API to detect objects and return the result in object
        if counter == 100:
            cv2.imwrite(filename='temp.jpg', img=frame)
            object = object_detection('temp.jpg')
            counter = 0
        else:
            counter += 1

        # display the results from the API
        display_objects(object, 'temp.jpg')
    
    cv2.imshow('Object Detector', frame)
    
    # capture keystroke
    k = cv2.waitKey(1)
    # if space bar key is pressed, toggle if statement above
    if k%256 == 32: 
        button_pressed = not(button_pressed)   
    # if esc key is pressed, quit program
    elif k%256 == 27: 
        break
    # if f key is pressed, flip image across x axis
    elif k%256 == 102:
        flip = not(flip)
    
# After the loop release the camera object 
vid.release() 
# Destroy all the windows 
cv2.destroyAllWindows() 