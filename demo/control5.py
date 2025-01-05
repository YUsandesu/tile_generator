import py5_tools
py5_tools.add_jars('./jars')
import py5
from controlP5 import ControlP5, Slider

def setup():
    global cp5
    py5.size(720, 485)
    cp5 = ControlP5(py5.get_current_sketch())
    (
        cp5.addTextfield('alias')
        .setPosition(500,20)
        .setSize(200,25)
        .setValue(80)
    )
    (
        cp5.addSlider('eye distance')
        .setPosition(500,80)
        .setSize(200,20)
        .setRange(30,120)
        .setValue(80)
    )
    (
        cp5.addKnob('eye size')
        .setPosition(515,135)
        .setRadius(35)
        .setRange(10,60)
        .setValue(50)
    )
    (
        cp5.addToggle('heavy brow')
        .setPosition(635,138)
        .setSize(20,20)
    )
    (
        cp5.addToggle('sleepless')
        .setPosition(635,185)
        .setSize(20,20)
    )
    (
        cp5.addSlider2D('nose position')
        .setPosition(500,240)
        .setSize(200,100)
        .setMinMax(-30,-20,30,20)
        .setValue(0,0)
    )

    (
        cp5.addSlider('mouth width')
        .setPosition(500,375)
        .setSize(200,20)
        .setRange(10,200)
        .setValue(124)
        .setNumberOfTickMarks(6)
        .setSliderMode(Slider.FLEXIBLE)
    )
    (
        cp5.getController('mouth width')
        .getCaptionLabel()
        .align(ControlP5.LEFT, ControlP5.BOTTOM_OUTSIDE)
        .setPaddingX(0)
        .setPaddingY(12)
    )
    (
        cp5.addButton('save image')
        .setPosition(500,440)
        .setSize(200,25)
        .setCaptionLabel('Save Image')
        .onClick(lambda e: py5.save('output_image.png'))
        # .onClick(lambda e: py5.save(cp5.getController('alias').getText()))
        # .onClick(lambda e: py5.println(e.getController().getInfo()))
    )
    
def draw():
    py5.background('#004477')
    py5.stroke('#FFFFFF')
    py5.stroke_weight(3)
    axis = 250
    
    py5.no_fill()
    py5.ellipse(axis, 220, 370, 370)
    
    # alias 
    py5.fill('#FFFFFF')
    py5.text_size(20)
    py5.text_align(py5.CENTER)
    alias = cp5.getController('alias').getText()
    py5.text(alias, axis, 450)
    py5.no_fill()
    
    # eyes
    eye_distance = cp5.getController('eye distance').getValue()
    eye_size = cp5.getController('eye size').getValue()
    py5.ellipse(axis-eye_distance,180, eye_size,eye_size)
    py5.ellipse(axis+eye_distance,180, eye_size,eye_size)
    
    if cp5.getController('heavy brow').getValue():
        py5.fill('#004477')
        py5.stroke('#004477')
        py5.rect(100,180-eye_size/2, 300,eye_size/2)
        py5.stroke('#FFFFFF')
        py5.line(
          axis-eye_distance-eye_size/2-5, 180,
          axis+eye_distance+eye_size/2+5, 180
        )

    if cp5.getController('sleepless').getValue():
        py5.no_fill()
        py5.arc(axis-eye_distance,190, eye_size,eye_size, 0,py5.HALF_PI)
        py5.arc(axis+eye_distance,190, eye_size,eye_size, py5.HALF_PI,2.5)
        py5.fill('#004477')
        
    # nose
    nose_position = cp5.getController('nose position')
    nose_x = nose_position.getArrayValue()[0]
    nose_y = nose_position.getArrayValue()[1]
    py5.line(axis-10+nose_x,180+nose_y, axis-10+nose_x,300+nose_y)
    py5.line(axis-10+nose_x,300+nose_y, axis-10+nose_x+30,300+nose_y)

    # mouth
    mouth_width = cp5.getController('mouth width').getValue()
    py5.line(axis-mouth_width/2,340, axis+mouth_width/2,340)
    
    
py5.run_sketch()