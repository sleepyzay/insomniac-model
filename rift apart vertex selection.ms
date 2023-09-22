global vertexSelectionArray = #(
	[ 513 ,  5 ],
[ 233 ,  5 ],
[ 2 ,  8 ],
[ 27 ,  13 ],
[ 153 ,  28 ],
[ 7 ,  2 ],
[ 1 ,  6 ]
)

fn selectVertices head vertexSelectionArray beginningIndex = (
	actionMan.executeAction 0 "40839"  -- MAX Script: MAXScript Editor
	clearlistener()
	vertsToSelect = #()
	vertexIndex = beginningIndex
	
	for x=1 to vertexSelectionArray.count  do (	--vertSelectionArray.count 
		vertexSkip = vertexSelectionArray[x][1]
		vertexRead = vertexSelectionArray[x][2]
		
		vertexIndex += vertexSkip
		vertexRange = vertexRead
		vertexEndIndex = vertexRange + vertexIndex
		
		format "skip: %  start: %    range: %   end: %\n" vertexSkip vertexIndex vertexRange vertexEndIndex

		
		for y=vertexIndex to vertexEndIndex do (
			append vertsToSelect y
		)
-- 		
		vertexIndex = vertexEndIndex
		
		
	)
	head.selectedVerts = vertsToSelect
)

head = selection[1]
try(destroydialog SliderValueRollout)catch()
rollout SliderValueRollout "Slider Value Example"
(
    spinner startSpinner "Start Value: " range:[-10000,10000,0]
    spinner rangeSpinner "Range: " range:[0,10000,50000]
	spinner sliderValue "Slider Value" range:[0,10000,0] type:#integer scale:1
    slider mySlider "My Slider" range:[startSpinner.value, startSpinner.value + rangeSpinner.value, startSpinner.value] type:#integer

    label valueLabel "Value:"
	
	on SliderValueRollout open do (
		selectVertices head vertexSelectionArray mySlider.value
	)
	
	on sliderValue changed val do (
		mySlider.value = sliderValue.value
		selectVertices head vertexSelectionArray mySlider.value
	)

    on mySlider changed val do
    (
        valueLabel.text = "Value: " + val as string
		selectVertices head vertexSelectionArray mySlider.value
		sliderValue.value = mySlider.value
    )
    
    on startSpinner changed val do
    (
        mySlider.range = [startSpinner.value, startSpinner.value + rangeSpinner.value, startSpinner.value]
    )
    
    on rangeSpinner changed val do
    (
        mySlider.range = [startSpinner.value, startSpinner.value + rangeSpinner.value, startSpinner.value]
    )
)

clearlistener()

createDialog SliderValueRollout










