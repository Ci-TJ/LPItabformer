### MathFeature for k-mer of lncRNAs and proteins
### Could be under env base and NGS


echo ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ $(date)~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
echo ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ $(date)~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

##0 Setting work directory and download files
WD=/home/user_li/linqin_tmp/Dataset/BioGram/compare/pj231220/   #Make sure your work directory
methD=/home/user_li/linqin_tmp/Dataset/BioGram/compare/test/MathFeature-master/methods

out1=3mer_gencode.v39_lncrna_hsa.csv
out2=1mer_UP000005640_prot_hsa.csv

if [[ -d $WD/feature ]]; then
	echo $WD/feature exit! 
else
	echo $WD/feature && mkdir $WD/feature
fi


#lncRNA 3mer
if [[ -f $WD/feature/$out1 ]]; then
	echo $WD/feature/$out1 exit! 
else
	echo $WD/feature/$out1 Not exit!
	python3 $methD/ExtractionTechniques.py -i $WD/sequence/gencode.v39_lncrna_seq.fa -o $WD/feature/$out1 -l RNA -t TNC -seq 2  && echo $out1 OK! # -seq 1 for DNA and 2 for RNA, -l just for label, could be anyone
fi

#protein 1mer
if [[ -f $WD/feature/$out2 ]]; then
	echo $WD/feature/$out2 exit! 
else
	echo $WD/feature/$out2 Not exit!
	python3 $methD/ExtractionTechniques-Protein.py -i $WD/sequence/UP000005640_79740_uniprot_hsa_prot_seq.fa -o $WD/feature/$out2 -l Protein -t AAC  && echo $out2 OK! # -l just for label, could be anyone
fi

echo ALL Done!
echo ====================================================== $(date) ======================================================
echo ====================================================== $(date) ======================================================
