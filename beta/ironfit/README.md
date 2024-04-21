# pyXspec での自動スペクトルフィット


'script/fit_xrsmres_iron_lines.py' がフィット本体で、'./script/fit_xrsmres_iron_lines.py' がサンプルを実施するスクリプトである。

"""
./script/fit_xrsmres_iron_lines.py \
	--inputpha $SAMPLE_DIR/input.pha \
	--rmf $SAMPLE_DIR/detector.rmf \
	--arf $SAMPLE_DIR/detector.arf \
	--param script/xspec_FeKalpha_param.yaml \
	--outname velax1_feKa_fit \
"""

で実行できる。ファイルは適宜、書き換えてほしい。

* --inputpha $SAMPLE_DIR/input.pha：入力のスペクトルファイル
* --rmf $SAMPLE_DIR/detector.rmf：rmf レスポンスファイル
* --arf $SAMPLE_DIR/detector.arf：arf レスポンスファイル
* --param script/xspec_FeKalpha_param.yaml：フィットのモデルやパラメータ初期値を入れた yaml ファイル
* --outname velax1_feKa_fit：フィット結果の図(pdf)やフィット結果を収容した結果(yaml)のファイル名。


