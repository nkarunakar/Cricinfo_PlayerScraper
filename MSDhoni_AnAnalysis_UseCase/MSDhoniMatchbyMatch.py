import pandas as pd
import matplotlib.pyplot as plt


if __name__ == "__main__":
    dussen_data=pd.read_csv("C:\Cricket\MS_Dhoni.csv")
    dussen_data=dussen_data.fillna(0)
   
    for id in dussen_data[(dussen_data["OVER"]>40) & (dussen_data["RRR"] >= 6) & (dussen_data["WON"]==1)].MID.unique():
        #plt.plot(dussen_data[dussen_data["MID"]==id].OVER,dussen_data[dussen_data["MID"]==id].CSR,label="Dussen")
        label1=str(id)+"_MSDhoni_ACtualSR"
        label2=str(id)+"_RRR"
        label3=str(id)+"_P2_ACtualSR"
        plt.plot(dussen_data[(dussen_data["MID"]==id) & (dussen_data["OVER"]>40) ].OVER,dussen_data[(dussen_data["MID"]==id) & (dussen_data["OVER"]>40)].RRR,label=label2,linestyle="--")
        plt.plot(dussen_data[(dussen_data["MID"]==id) & (dussen_data["OVER"]>40) ].OVER,dussen_data[(dussen_data["MID"]==id) & (dussen_data["OVER"]>40)].CSR,label=label1)
        plt.plot(dussen_data[(dussen_data["MID"]==id) & (dussen_data["OVER"]>40) ].OVER,dussen_data[(dussen_data["MID"]==id) & (dussen_data["OVER"]>40)].OBCSR,label=label3)
        plt.legend()
        plt.show()

