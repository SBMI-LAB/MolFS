#ifndef SEQFILTER_H
#define SEQFILTER_H

#include<QVector>
#include <QList>
#include<QString>
#include <QDebug>
#include <QFile>
#include <QDir>
#include <tuple>
#include <string.h>
#include <sys/stat.h>



struct DomainPosInfo{
    int Pos;
    float score;
};

class SeqFilter
{
public:
    /// Flags
    std::string F_folder;
    std::string W_folder;


    QVector<QString> Primers;
    QVector<QString> Terminators;

    QFile * FilterFile;

    SeqFilter();

    void RunAnalysis();
    QString seqrcomplement(QString seq);
    void ReadPrimers();
    void ReadSeqFiles();
    void ReadFastQFile(QString filename);
    DomainPosInfo searchSeqSSW(QString dom, QString seq);

    void CloseFiles();

    bool analyzeseq(QString seq);


};

#endif // SEQFILTER_H
