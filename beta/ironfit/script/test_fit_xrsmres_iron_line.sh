#!/bin/sh -f

#ls $SAMPLE_DIR/input.pha
#ls $SAMPLE_DIR/detector.rmf 
#ls $SAMPLE_DIR/detector.arf 

./script/fit_xrsmres_iron_lines.py \
	--inputpha $SAMPLE_DIR/input.pha \
	--rmf $SAMPLE_DIR/detector.rmf \
	--arf $SAMPLE_DIR/detector.arf \
	--param script/xspec_FeKalpha_param.yaml \
	--outname velax1_feKa_fit \
