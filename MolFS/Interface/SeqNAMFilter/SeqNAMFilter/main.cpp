#include <QCoreApplication>
#include <stdio.h>
#include "seqfilter.h"
#include <string.h>
#include <iostream>
#include <sys/stat.h>
#include <QDebug>


using std::string;
using std::cout;




string format_directory(const std::string &s)
{
    char L = s[s.size()-1];
    string ns = "";

    if (L != '/')
        ns = s + "/";
    else
        ns = s;

    return ns;
}

bool is_directory(const std::string &s)
{
  struct stat buffer;
  return (stat (s.c_str(), &buffer) == 0);
}


int main(int argc, char *argv[])
{
    //// Parameters
    /// -f Folder:  Source folder of fastq files        [1]
    /// -w Folder:  Working directory. Default /tmp/    [2]



    string F_folder = "/home/acroper/Downloads/SeqNAM/Completed/pass/";
    string W_folder = "/tmp/SeqNAM2";


    int preCommand = 0;

    for (int i = 0; i < argc; i++)
    {
        string args = (string) argv[i];
        if (preCommand == 0)
        {

            if (args == "-f")
                preCommand = 1;

            if (args == "-w")
                preCommand = 2;


        }
        else
        {
            switch (preCommand) {

            case 1: /// should check existence of folder
                F_folder = argv[i];
                break;
            case 2: /// should check existence of folder
                W_folder = argv[i];
                break;


            }
            preCommand = 0;
        }
    }


    SeqFilter Seq = SeqFilter();

    F_folder = format_directory(F_folder);
    W_folder = format_directory(W_folder);

    bool Passed = true;

    cout << "\n\nValidating parameters:\n";
    /// Check parameters
    if (!is_directory(F_folder))
    {
        Passed = false;
        cout << "Invalid FastQ folder \n";
    }

    if (!is_directory(W_folder))
    {
        Passed = false;
        cout << "Invalid working folder \n";
    }



    if (Passed)
    {
        cout << "All parameters valid, proceeding to run analysis\n";
    }

    Seq.F_folder = F_folder;
    Seq.W_folder = W_folder;

    cout  << "Fastq Folder    -f : " << F_folder << "\n";
    cout  << "Working Folder  -w : " << W_folder << "\n";



    /// Run decoder

    if (Passed)
        Seq.RunAnalysis();


    printf("Finish\n");



}
