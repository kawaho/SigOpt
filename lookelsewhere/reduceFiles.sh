for i in `seq 155 155`
do
 hadd higgsCombinemass${i}cToy.Significance.mH${i}.123456.root *mass${i}Toy*root
 rm *mass${i}Toy*root
done
