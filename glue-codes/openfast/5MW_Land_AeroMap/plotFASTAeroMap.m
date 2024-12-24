function [Channels, ChannelNames, ChannelUnits] = plotFASTAeroMap(fileName)
%     fileName = 'AeroMap.outb';
    
    
    [Channels, ChannelNames, ChannelUnits] = ReadFASTbinary(fileName);
    %%
    Y_indx = find(strcmp(ChannelNames,'Pitch'),1,"first");
    X_indx = find(strcmp(ChannelNames,'TSR'),1,"first");
    [X, Y, Z, indx] = getGriddedData(Channels, X_indx, Y_indx);
%%
    figure;
    tiledlayout(3,5)
    for i=1:length(Z)
        nexttile;
        if strcmpi(ChannelNames(indx{i}),'RtAeroCp')
            mn = max(-0.5,min(Channels(:,indx{i})));
            mx = max(Channels(:,indx{i}));
            dx = min(mx,0.7)/20;
            contourf(X,Y,Z{i},[mn 0:dx:0.7 mx])
        else
            contourf(X,Y,Z{i},25);
        end
        xlabel([ChannelNames{X_indx} ' ' ChannelUnits{X_indx}]);
        ylabel([ChannelNames{Y_indx} ' ' ChannelUnits{Y_indx}])
        title( [ChannelNames{indx{i}} ' ' ChannelUnits{indx{i}}]);
        colorbar
    end

end

function [x1, y1, Z, indx] = getGriddedData(Channels, X_indx, Y_indx)

    x = unique(Channels(:,X_indx), "sorted");
    y = unique(Channels(:,Y_indx), "sorted");
 %%
    ic=0;
    [x1,y1] = meshgrid(x, y);
    for i=2:size(Channels,2) 
        if i~=X_indx && i~=Y_indx
            ic = ic+1;
            Z{ic}=griddata(Channels(:,X_indx), Channels(:,Y_indx), Channels(:,i), x1, y1,'nearest');
            indx{ic}=i;
        end
    end

  end

