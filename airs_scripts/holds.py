from . import rotateHold

def calculate(trk, rad, std):
    track = trk
    track = ((track + 180) % 360)
    radial = rad
    toFlag = ((radial + 180) % 360)

    answer = std
    if answer in ('y', 'yes', 's','standard'):
        direction = 1
    elif answer in ('n', 'no'):
        direction = 0

    
    if direction == 1:
        directToTeardrop = ((radial + 110) % 360)

        directToParallel = ((radial - 70) % 360)

        parallelToTeardrop = ((radial + 180) % 360)

        #Conversions: radConvert = radial to base 180. trackConvert = track to base 180 track. 
        radConvert = ((radial - 180)  % 180)
        trackConvert = ((track - radConvert) % 360)

        imageConvert = ((trackConvert - 180) % 360)
        image_path = "holdsRight.png"
        degrees = int(imageConvert)
        overlay_path = "whitePlane.png"
        try:
            holdPic = rotateHold.rotate_and_overlay_image(image_path, degrees, overlay_path)
            #holdPic.show()
        except Exception as e:
            print(e)
            holdPic = None
        
        if 110 < trackConvert < 290:
            sector = 3
            
            instruction = 'DIRECT TO'
            if trackConvert >= 270:
                offset = ((radial - 90) % 360)
                
                instruction = f'20s: {offset}, 30s: ↱, 40s: OUTB'

        elif 290 < trackConvert < 359:
        
            sector = 1
            offset = ((radial - 30)% 360)
            
            instruction = f'1m: {offset}, TO STN: ↷ {toFlag}'


        elif trackConvert < 110:
            sector = 2

            instruction = f'1m: {radial}, DCT TO STN: ↶'
            

    elif direction == 0:
        
        directToTeardrop = ((radial - 110) % 360)

        directToParallel = ((radial + 70) % 360)

        parallelToTeardrop = ((radial + 180) % 360)

        radConvert = ((radial - 180)  % 360)

        #Conversions: radConvert = radial to base 180. trackConvert = track to base 180 track.  
        radConvert = ((radial - 180)  % 180)
        trackConvert = ((track - radConvert) % 360)
        
        imageConvert = ((trackConvert - 180) % 360)
        image_path = "holdsLeft.png"
        degrees = int(imageConvert)
        overlay_path = "whitePlane.png"
        try:
            holdPic = rotateHold.rotate_and_overlay_image(image_path, degrees, overlay_path)
            #holdPic.show()
        except Exception as e:
            print(e)
            holdPic = None


        if 70 < trackConvert < 250:
            sector = 3

            instruction = 'DCT TO'
            if trackConvert <= 90:
                offset = ((radial + 90) % 360)

                instruction = f'20s: {offset}, 30s: ↰, 40s: OUTB'

        elif 250 < trackConvert < 359 or trackConvert == 0:
            sector = 2

            instruction = f'1m: {radial}, DCT TO STN: ↷'
        
        elif trackConvert < 70:
            sector = 1
            offset = ((radial + 30)% 360)

            instruction = f'1m: {offset}, TO STN: ↶ {toFlag}'

    return holdPic, toFlag, sector, instruction, directToTeardrop, directToParallel, parallelToTeardrop, 








    
