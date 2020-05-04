x = dir('*.sbx');

for i = 1:size(x,1)
   y = x(i).name;
   sbx2h5(y(1:end-4));
end 
% y = x(1).name;
% sbx2tif(y(1:14));
