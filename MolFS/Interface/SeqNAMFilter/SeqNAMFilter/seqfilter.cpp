#include "seqfilter.h"

#include <QDebug>
#include <QFile>
#include <QDir>

#include <iostream>
#include <thread>
#include <math.h>

#include "ssw_cpp.h"

using std::string;
using std::cout;
using std::endl;
using std::tuple;


SeqFilter::SeqFilter()
{

}

void SeqFilter::RunAnalysis()
{

    ReadPrimers();
    ReadSeqFiles();
    CloseFiles();

}


QString SeqFilter::seqrcomplement(QString seq){
    QString rseq = "";

    for (int i = 0; i < seq.size(); i++) {

        if (seq.at(i) == QChar('A'))
            rseq.prepend("T");
        if (seq.at(i) == QChar('T'))
            rseq.prepend("A");
        if (seq.at(i) == QChar('C'))
            rseq.prepend("G");
        if (seq.at(i) == QChar('G'))
            rseq.prepend("C");

    }



    return rseq;

}

void SeqFilter::ReadPrimers(){

    QFile inputFile("Primers.txt");
    if (inputFile.open(QIODevice::ReadOnly))
    {
       QTextStream in(&inputFile);
       while (!in.atEnd())
       {
          QString line = in.readLine();
          Primers.append(line);
       }
       inputFile.close();
    }

    QFile inputFile2("Terminators.txt");
    if (inputFile2.open(QIODevice::ReadOnly))
    {
       QTextStream in(&inputFile2);
       while (!in.atEnd())
       {
          QString line = in.readLine();
          Terminators.append(line);
       }
       inputFile2.close();
    }


    /// Prepare the output file
    QString filename = QString::fromUtf8( W_folder.c_str()) + QString("FilteredSeqNAM.fastq");

    FilterFile = new QFile(filename);
    FilterFile->open(QIODevice::WriteOnly | QIODevice::Text);

    qDebug() << "Creating output file at " << filename << "\n";

    //QTextStream out2(FilterFile);
    //out2 << "Sequence\n" ;


}


void SeqFilter::ReadSeqFiles() {


    QString Location = QString::fromUtf8( F_folder.c_str());

    QDir directory (Location);

    int p = 0;

    QStringList Sequences = directory.entryList(QStringList() << "*.fastq",QDir::Files);

    int Total = Sequences.size();

    cout << "Progress: " << 0 <<  endl;



    foreach(QString filename, Sequences) {

        ReadFastQFile(Location + filename);

        p++;

        float Progress =  ((float) 100*p)/Total;

        cout << "Progress: " << Progress << endl;


    }

}

void SeqFilter::ReadFastQFile(QString filename){


    qDebug() <<"Reading file "<<filename << "\n";

    QFile inputFile(filename);

    if (inputFile.open(QIODevice::ReadOnly))
    {
       QTextStream in(&inputFile);

       int pos = 1;

       while (!in.atEnd())
       {
          in.readLine();  //First id
          QString line = in.readLine();  //sequence


          QString rline = seqrcomplement(line);


          bool success = analyzeseq(line);
          if (!success)  // Omit if it was valid
            analyzeseq(rline);

          in.readLine();  // +
          in.readLine();  // last value

          pos ++;






       }
       inputFile.close();
    }

}


DomainPosInfo SeqFilter::searchSeqSSW(QString dom, QString seq){

    int pos = -1;

    DomainPosInfo Res;

    QString clist;


    string ref   = seq.toUtf8().constData(); //"CAGCCTTTCTGACCCGGAAATCAAAATAGGCACAACAAA";
    string query = dom.toUtf8().constData(); //"CTGAGCCGGTAAATC";
    int32_t maskLen = strlen(query.c_str())/2;
    maskLen = maskLen < 15 ? 15 : maskLen;

    // Declares a default Aligner
    StripedSmithWaterman::Aligner aligner;
    // Declares a default filter
    StripedSmithWaterman::Filter filter;
    // Declares an alignment that stores the result
    StripedSmithWaterman::Alignment alignment;
    // Aligns the query to the ref
    aligner.Align(query.c_str(), ref.c_str(), ref.size(), filter, &alignment, maskLen);

    int len = alignment.ref_end - alignment.ref_begin ;
    float score = 0;


        string nref = ref.substr(alignment.ref_begin, len);
        string nquery = query.substr(alignment.query_begin, len);


        score = 1-((float)alignment.mismatches/len);
        //score = (dom.size()-((float)alignment.mismatches))/dom.size();

        //if (score > 0.9)
        //{

        // Get the real alignment score
        int matches = 0;
        int mismatches = 0;

        for (int i = 0; i < dom.size(); i++)
        {
            if ( query[i] == ref[alignment.ref_begin + i]  )
                matches ++;
            else
                mismatches ++;
        }

        score = 1 - ( float ) ( mismatches )/(dom.size()) ;


        pos = alignment.ref_begin;



            //clist = getCigarAlign(QString(nref.c_str()), QString(nquery.c_str()), alignment.cigar);

        //}

        //if (score < 0.85)
        //    pos = -1;



    Res.Pos = pos;

    Res.score = score;

    return Res;

}



bool SeqFilter::analyzeseq(QString seq){

    if (seq.size() < 290)
        return false;

    int MaxScore = -1;

    DomainPosInfo Sel;

    int Option = 0;

    for (int i=0; i < Primers.size(); i++){

        DomainPosInfo pos = searchSeqSSW(Primers[i], seq);

        if (pos.score > MaxScore)
        {
            MaxScore = pos.score;
            Sel.Pos = pos.Pos;
            Sel.score = pos.score;
            Option = i;
        }

    }

    if (MaxScore < 0.8)
        return false;

    // else

    /// Process the data now
    ///
    /// In sel should be sequence that was aligned for the primer
    /// We should attemp to align the terminator too and then reconstruct
    /// the sequence with the proper dimensions.
    ///

    DomainPosInfo pos2 = searchSeqSSW(Terminators[Option], seq);

    int mSize =  pos2.Pos -  Sel.Pos + Primers[Option].size();
    if (mSize < 245 )
        return false;

    /// Now we should trim the sequence
    QString BaseDat1 =  Primers[Option]+ seq.mid(Sel.Pos +  Primers[Option].size(), pos2.Pos) + Terminators[Option] + "\n" ;

    /// Write to the output file
    QTextStream out2(FilterFile);

    out2 << "@\n";
    out2 << BaseDat1;
    out2 << "+\n$\n";


    return true; // Passed


}


void SeqFilter::CloseFiles() {
    FilterFile->close();
}






