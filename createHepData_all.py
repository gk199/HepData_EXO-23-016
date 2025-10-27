#!/usr/bin/env python3
"""
HEPData Generator for ROOT Files

This script extracts histograms from ROOT files and converts them to HEPData format.
It reads a ROOT file containing a TCanvas with multiple histograms and generates
the appropriate YAML files for HEPData submission.

For EXO-23-016

Usage:
    python3 createHepData_all.py

Output:
    - Creates 'hepdata_output/' directory with YAML files
    - Creates 'hepdata_submission.tar.gz' archive for submission

Dependencies:
    - ROOT (PyROOT)
    - hepdata_lib
    - readTest.py (for histogram extraction from canvas)
"""

from __future__ import print_function
import ROOT
import os
import sys
import yaml
import shutil
import subprocess
from hepdata_lib import RootFileReader, Submission, Variable, Uncertainty, Table

# Import the helper function from readTest.py
sys.path.append('.')
from readTest import collect_hists_from_canvas


def makeVariable(plot, label, is_independent, is_binned, is_symmetric, units, CME=13.6, uncertainty=True):
    var = Variable(label, is_independent=is_independent, is_binned=is_binned, units=units)
    var.values = plot["y"]
    if uncertainty:
        unc = Uncertainty("", is_symmetric=is_symmetric)
        unc.values = plot["dy"]
        var.add_uncertainty(unc)
    var.add_qualifier("SQRT(S)", CME, "TeV")
    #var.add_qualifier("HLT rate","2016")                                                                                                                                          
    return var

def check_imagemagick_available():
    """Check if ImageMagick convert command is available"""
    try:
        # Try to run ImageMagick convert command
        result = subprocess.run(['convert', '-version'], 
                              capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
        return False

def makeHcalTowerEffTable():
    table = Table("L1T HCAL tower efficiency vs Timing shift [ns]")
    table.description = "The L1T HCAL trigger tower efficiency of the timing-flagged towers in 2023 HCAL timing-scan data: HCAL delayed timing tower efficiency "\
        "during an HCAL timing phase scan during 2023, with efficiencies split by trigger towers centered at $\\eta\\approx 0$ (blue circles), 0.65 (red squares), "\
        "1.26 (black triangles), and with width $\\Delta \\eta = 0.087$. The sharp turn-on between timing delays of 0-6 ns is expected, as the prompt timing "\
        "range includes pulses up to and including those recorded at a 6 ns arrival time (reported in half-ns steps by the TDC), demonstrating the timing "\
        "trigger performance. The timing-flagged towers must have at least one delayed cell, no prompt cells, and energy ${>}4$ GeV. The efficiency is calculated "\
        "relative to towers with any valid timing code, meaning the tower contains at least one cell with energy ${>}4$ GeV and a TDC code of prompt, slightly delayed, "\
        "or very delayed. Multiple flagged towers are required for the HCAL-based displaced- and delayed-jet L1T to be set, and this shows the turn-on at a per-tower "\
        "level relative to incoming pulse timing."
    image = "data_Gillian/QIE_Tower_ieta_fg123_effs_diff_ieta_nopreliminary.pdf"
    reader = RootFileReader("data_Gillian/QIE_Tower_ieta_fg123_effs_diff_ieta.root")
    # Tefficiencies from the ROOT file
    eta0 = "time_flagged_eta_0;1"
    eta0pt65 = "time_flagged_eta_0.65;1"
    eta1pt26 = "time_flagged_eta_1.26;1"
    table.location = "Data from Fig. 21"
    table.add_image(image)

    plot_eta0 = reader.read_teff(eta0)
    plot_eta0pt65 = reader.read_teff(eta0pt65)
    plot_eta1pt26 = reader.read_teff(eta1pt26)

    xAxisVar = Variable("Timing shift", is_independent=True, is_binned=False, units="ns")
    xAxisVar.values = plot_eta0["x"]
    table.add_variable(xAxisVar)

    table.add_variable(makeVariable(plot=plot_eta0, label="Time flagged, $\eta=0$", is_independent=False, is_binned=False, is_symmetric=False, units=""))
    table.add_variable(makeVariable(plot=plot_eta0pt65, label="Time flagged, $\eta=0.65$", is_independent=False, is_binned=False, is_symmetric=False, units=""))
    table.add_variable(makeVariable(plot=plot_eta1pt26, label="Time flagged, $\eta=1.26$", is_independent=False, is_binned=False, is_symmetric=False, units=""))

    return table

def makeHcalLLPflaggedJetEffTable():
    table = Table("L1T efficiency of LLP-flagged jets vs L1 jet ET [GeV]")
    table.description = "The L1T efficiency of the LLP jet trigger in 2023 HCAL timing-scan data: The HCAL LLP-flagged L1T trigger delayed jet fraction versus jet "\
        "$E_T$ during the 2023 HCAL phase scan demonstrates that the delayed jet fraction approaches unity as the timing shift, with units in ns, is increased. The figure "\
        "shows results inclusive in pseudorapidity for the HCAL barrel, corresponding to $|{\\eta}| < 1.35$. The fraction of LLP-flagged L1 jets is compared to all L1 jets "\
        "from a data set of events enriched with jets or $p_T^{\\text{miss}}$. No explicit selection criterion is applied on the jet ET, though the implicit requirement for a jet to "\
        "have at least two cells with $E_T > 4$ GeV shapes the resulting jet turn-on curve."
    image = "data_Gillian/Jet_Et_all_delay_nopreliminary.pdf"
    reader = RootFileReader("data_Gillian/Jet_Et_all_delay.root")
    # Tefficiencies from the ROOT file
    timing_m4 = "timing_shift_-4ns;1"
    timing_m2 = "timing_shift_-2ns;1"
    timing_0 = "timing_shift_0ns;1"
    timing_2 = "timing_shift_2ns;1"
    timing_4 = "timing_shift_4ns;1"
    timing_6 = "timing_shift_6ns;1"
    timing_8 = "timing_shift_8ns;1"
    timing_10 = "timing_shift_10ns;1"
    table.location = "Data from Fig. 22"
    table.add_image(image)

    plot_timing_m4 = reader.read_teff(timing_m4)
    plot_timing_m2 = reader.read_teff(timing_m2)
    plot_timing_0 = reader.read_teff(timing_0)
    plot_timing_2 = reader.read_teff(timing_2)
    plot_timing_4 = reader.read_teff(timing_4)
    plot_timing_6 = reader.read_teff(timing_6)
    plot_timing_8 = reader.read_teff(timing_8)
    plot_timing_10 = reader.read_teff(timing_10)

    xAxisVar = Variable("L1 jet ET", is_independent=True, is_binned=False, units="GeV")
    xAxisVar.values = plot_timing_m4["x"]
    table.add_variable(xAxisVar)

    table.add_variable(makeVariable(plot=plot_timing_m4, label="Timing shift = -4 ns", is_independent=False, is_binned=False, is_symmetric=False, units=""))
    table.add_variable(makeVariable(plot=plot_timing_m2, label="Timing shift = -2 ns", is_independent=False, is_binned=False, is_symmetric=False, units=""))
    table.add_variable(makeVariable(plot=plot_timing_0, label="Timing shift = 0 ns", is_independent=False, is_binned=False, is_symmetric=False, units=""))
    table.add_variable(makeVariable(plot=plot_timing_2, label="Timing shift = 2 ns", is_independent=False, is_binned=False, is_symmetric=False, units=""))
    table.add_variable(makeVariable(plot=plot_timing_4, label="Timing shift = 4 ns", is_independent=False, is_binned=False, is_symmetric=False, units=""))
    table.add_variable(makeVariable(plot=plot_timing_6, label="Timing shift = 6 ns", is_independent=False, is_binned=False, is_symmetric=False, units=""))
    table.add_variable(makeVariable(plot=plot_timing_8, label="Timing shift = 8 ns", is_independent=False, is_binned=False, is_symmetric=False, units=""))
    table.add_variable(makeVariable(plot=plot_timing_10, label="Timing shift = 10 ns", is_independent=False, is_binned=False, is_symmetric=False, units=""))

    return table

def makeHcalL1JetHTEffTable(xvar):
    if xvar == "HT": 
        name = "event $H_T$"
        image = "data_Gillian/Plotefficiency_eventHT_log_HLT_v3_MC_eventHT_L1effs_noprelim.pdf"
        location = "left"
        reader = RootFileReader("data_Gillian/Figures_Plotefficiency_eventHT_log_HLT_v3_MC_eventHT_L1effs.root")
    if xvar == "jet": 
        name = "jet $p_T$"
        image = "data_Gillian/Plotefficiency_perJet_Pt_log_HLT_v3_MC_L1effs_noprelim.pdf"
        location = "right"
        reader = RootFileReader("data_Gillian/Figures_Plotefficiency_perJet_Pt_log_HLT_v3_MC_L1effs.root")
    table = Table("L1T efficiency of HCAL based-LLP triggers vs. " + name)
    table.description = "The L1T efficiency of the HCAL-based LLP jet triggers, as a function of event $H_T$ (left) and jet $p_T$ (right), for $H \\to SS \\to "\
        "b\\bar{b}b\\bar{b}$ events with $m_{H}=350$ GeV, $m_{S}=80$ GeV, and $c\\tau_{S}=0.5$ m (light blue circles) and $m_{H}=125$ GeV, $m_{S}=50$ GeV, and "\
        "$c\\tau_{S}=3$ m (purple triangles), for 2023 conditions. The trigger efficiency is evaluated for LLPs decaying in HB depths 3 or 4, corresponding to "\
        "$214.2< R<295$ cm and $|{\\eta}|< 1.26$. These LLPs are also required to be matched to an offline jet in HB."
    # Tefficiencies from the ROOT file
    if xvar == "HT": 
        LLP350 = "Plotefficiency_eventHT_log_HLT_v3_MC_eventHT_L1effs_350;1"
        LLP125 = "Plotefficiency_eventHT_log_HLT_v3_MC_eventHT_L1effs_125;1"
    if xvar == "jet": 
        LLP350 = "Plotefficiency_perJet_Pt_log_HLT_v3_MC_L1effs_350;1"
        LLP125 = "Plotefficiency_perJet_Pt_log_HLT_v3_MC_L1effs_125;1"
    table.location = "Data from Fig. 23 " + location
    table.add_image(image)
    plot_LLP350 = reader.read_teff(LLP350)
    plot_LLP125 = reader.read_teff(LLP125)

    if xvar == "jet": xAxisVar = Variable("Jet $pT$", is_independent=True, is_binned=False, units="GeV")
    if xvar == "HT": xAxisVar = Variable("$Event HT$", is_independent=True, is_binned=False, units="GeV")
    xAxisVar.values = plot_LLP350["x"]
    table.add_variable(xAxisVar)

    table.add_variable(makeVariable(plot=plot_LLP350, label="$m_H = 350$ GeV, $m_S = 80$ GeV, $c\\tau = 0.5$ m", is_independent=False, is_binned=False, is_symmetric=False, units=""))
    table.add_variable(makeVariable(plot=plot_LLP125, label="$m_H = 125$ GeV, $m_S = 50$ GeV, $c\\tau = 3$ m", is_independent=False, is_binned=False, is_symmetric=False, units=""))

    return table

def makeHcalL1DecayREffTable():
    table = Table("L1T efficiency of HCAL bsaed-LLP triggers vs. LLP decay R")
    table.description = "The L1T efficiency of the HCAL-based LLP jet triggers as a function of LLP decay radial position $R$ for $H \\to SS \\to b\\bar{b}b\\bar{b}$ events with "\
        "$m_{H}=350$ GeV, $m_{S}=80$ GeV, and $c\\tau_{S}=0.5$ m (light blue circles) and $m_{H}=125$ GeV, $m_{S}=50$ GeV, and $c\\tau_{S}=3$ m (purple "\
        "triangles), for 2023 conditions. The trigger efficiency is evaluated for LLPs within $|{\\eta}| <1.26$ where either the LLP or its decay products are matched to an "\
        "offline jet in HB with $p_T>100$ GeV."
    image = "data_Gillian/Plotefficiency_perJet_MatchedLLP_DecayR_log_HLT_v3_MC_jetE100_L1effs_noprelim.pdf"
    reader = RootFileReader("data_Gillian/Figures_Plotefficiency_perJet_MatchedLLP_DecayR_log_HLT_v3_MC_jetE100_L1effs.root")
    # Tefficiencies from the ROOT file
    LLP350 = "Plotefficiency_perJet_MatchedLLP_DecayR_log_HLT_v3_MC_jetE100_L1effs_lin;1"
    LLP125 = "Plotefficiency_perJet_MatchedLLP_DecayR_log_HLT_v3_MC_jetE100_L1effs_lin;2"
    table.location = "Data from Fig. 24"
    table.add_image(image)

    plot_LLP350 = reader.read_teff(LLP350)
    plot_LLP125 = reader.read_teff(LLP125)

    xAxisVar = Variable("LLP Decay R", is_independent=True, is_binned=False, units="cm")
    xAxisVar.values = plot_LLP350["x"]
    table.add_variable(xAxisVar)

    table.add_variable(makeVariable(plot=plot_LLP350, label="$m_H = 350$ GeV, $m_S = 80$ GeV, $c\\tau = 0.5$ m", is_independent=False, is_binned=False, is_symmetric=False, units=""))
    table.add_variable(makeVariable(plot=plot_LLP125, label="$m_H = 125$ GeV, $m_S = 50$ GeV, $c\\tau = 3$ m", is_independent=False, is_binned=False, is_symmetric=False, units=""))

    return table

def makeDisplacedMuonL1EffTable(xvar):
    table_title = xvar
    table = Table("L1T efficiency vs displaced muon $\mathrm{d_{0}}$ in "+table_title)

    if xvar=="BMTF":
        location = "upper left"
        table.description = "The BMTF L1T efficiencies for beamspot-constrained and beamspot-unconstrained $\mathrm{p_{T}}$ assignment " \
            "algorithms for L1T $\mathrm{p_{T}} > 10\mathrm{GeV}$ with respect to generator-level muon track $\mathrm{d_{0}}$, obtained " \
            "using a sample which produces LLPs that decay to dimuons. The L1T algorithms and data-taking conditions correspond to 2024. A selection " \
            "on the generator-level muon track $\mathrm{p_{T}} > 15\mathrm{GeV}$ is applied to show the performance at the efficiency plateau. The " \
            "generator-level muon tracks are extrapolated to the second muon station to determine the $\eta^{\mathrm{gen}}_{\mathrm{st2}}$ values that " \
            "are used in the plot. The solid markers show the new vertex-unconstrained algorithm performance, while the hollow markers show the default " \
            "beamspot-constrained algorithm performance."
        image = "data_Efe/Figure39_upper_left.pdf"
        reader = RootFileReader("data_Efe/Figure39_upper_left.root")
        prompt = "eff_dxy_BMTF;1"
        disp = "eff_dxy_NN_BMTF;1"
        label_prompt = "BMTF beamspot-constrained efficiency"
        label_disp = "BMTF beamspot-unconstrained efficiency"
    elif xvar=="OMTF":
        location = "upper right"
        table.description = "The OMTF L1T efficiencies for beamspot-constrained and beamspot-unconstrained $\mathrm{p_{T}}$ assignment " \
            "algorithms for L1T $\mathrm{p_{T}} > 10\mathrm{GeV}$ with respect to generator-level muon track $\mathrm{d_{0}}$, obtained " \
            "using a sample which produces LLPs that decay to dimuons. The L1T algorithms and data-taking conditions correspond to 2024. A selection " \
            "on the generator-level muon track $\mathrm{p_{T}} > 15\mathrm{GeV}$ is applied to show the performance at the efficiency plateau. The " \
            "generator-level muon tracks are extrapolated to the second muon station to determine the $\eta^{\mathrm{gen}}_{\mathrm{st2}}$ values that " \
            "are used in the plot. The solid markers show the new vertex-unconstrained algorithm performance, while the hollow markers show the default " \
            "beamspot-constrained algorithm performance."
        image = "data_Efe/Figure39_upper_right.pdf"
        reader = RootFileReader("data_Efe/Figure39_upper_right.root")
        prompt = "eff_dxy_OMTF;1"
        disp = "eff_dxy_NN_OMTF;1"
        label_prompt = "OMTF beamspot-constrained efficiency"
        label_disp = "OMTF beamspot-unconstrained efficiency"
    elif xvar=="EMTF":
        location = "lower"
        table.description = "The EMTF L1T efficiencies for beamspot-constrained and beamspot-unconstrained $\mathrm{p_{T}}$ assignment " \
            "algorithms for L1T $\mathrm{p_{T}} > 10\mathrm{GeV}$ with respect to generator-level muon track $\mathrm{d_{0}}$, obtained " \
            "using a sample which produces LLPs that decay to dimuons. The L1T algorithms and data-taking conditions correspond to 2024. A selection " \
            "on the generator-level muon track $\mathrm{p_{T}} > 15\mathrm{GeV}$ is applied to show the performance at the efficiency plateau. The " \
            "generator-level muon tracks are extrapolated to the second muon station to determine the $\eta^{\mathrm{gen}}_{\mathrm{st2}}$ values that " \
            "are used in the plot. The solid markers show the new vertex-unconstrained algorithm performance, while the hollow markers show the default " \
            "beamspot-constrained algorithm performance. In the EMTF plot, the different colors show different $|\eta|$ " \
            "regions: $1.24 < \eta^{\mathrm{gen}}_{\mathrm{st2}} < 1.6$ (blue), $1.6 < \eta^{\mathrm{gen}}_{\mathrm{st2}} < 2.0$ (red)."
        image = "data_Efe/Figure39_lower.pdf"
        reader = RootFileReader("data_Efe/Figure39_lower.root")
        prompt = "eff_dxy_EMTF1;1"
        disp = "eff_dxy_NN_EMTF1;1"
        prompt2 = "eff_dxy_EMTF2;1"
        disp2 = "eff_dxy_NN_EMTF2;1"
        label_prompt = "EMTF ($1.24 < \eta^{\mathrm{gen}}_{\mathrm{st2}} < 1.6$) beamspot-constrained efficiency"
        label_disp = "EMTF ($1.24 < \eta^{\mathrm{gen}}_{\mathrm{st2}} < 1.6$) beamspot-unconstrained efficiency"
        label_prompt2 = "EMTF ($1.6 < \eta^{\mathrm{gen}}_{\mathrm{st2}} < 2.0$) beamspot-constrained efficiency"
        label_disp2 = "EMTF ($1.6 < \eta^{\mathrm{gen}}_{\mathrm{st2}} < 2.0$) beamspot-unconstrained efficiency"
    else:
        raise ValueError("Unexpected input to function makeDelayedDiPhotonHistTable()")

    table.location = "Data from Fig. 39 "+location
    table.add_image(image)

    if xvar=="EMTF":
        plot_prompt = reader.read_graph(prompt)
        plot_disp = reader.read_graph(disp)
        plot_prompt2 = reader.read_graph(prompt2)
        plot_disp2 = reader.read_graph(disp2)
    else:
        plot_prompt = reader.read_graph(prompt)
        plot_disp = reader.read_graph(disp)

    xAxisVar = Variable("Gen.-level muon track d_{0}", is_independent=True, is_binned=False, units="cm")
    xAxisVar.values = plot_prompt["x"]
    table.add_variable(xAxisVar)

    table.add_variable(makeVariable(plot=plot_prompt, label=label_prompt, is_independent=False, is_binned=False, is_symmetric=False, units=""))
    table.add_variable(makeVariable(plot=plot_disp, label=label_disp, is_independent=False, is_binned=False, is_symmetric=False, units=""))
    if xvar=="EMTF":
        table.add_variable(makeVariable(plot=plot_prompt2, label=label_prompt2, is_independent=False, is_binned=False, is_symmetric=False, units=""))
        table.add_variable(makeVariable(plot=plot_disp2, label=label_disp2, is_independent=False, is_binned=False, is_symmetric=False, units=""))

    return table


def makeDelayedDiPhotonHistTable(xvar):
    table_title = 'barrel' if xvar=='eb' else 'endcap'
    table = Table("ECAL crystal seed time delay for LLP signature in "+table_title)

    if xvar=="eb":
        location = "left"
        table.description = "The ECAL time delay of the $\\mathrm{e/\\gamma}$ L1 seeds in the barrel. The distributions are "\
            "shown for $\\mathrm{Z\\ \\rightarrow\\ ee}$ simulation and $\\mathrm{\\chi^{0}\\ c\\tau}$ values of "\
            "$\\mathrm{3\\ cm,\\ 30\\ cm}$ and $\\mathrm{3\\ m}$, "\
            "assuming the singlet-triplet Higgs dark portal model ($\\mathrm{\\chi^{\\pm}\\ \\rightarrow\\ \\chi^{0} \\ell^{\\pm} \\nu}$, "\
            "where the $\\mathrm{\\chi^{\\pm}}$ has a mass of $\\mathrm{220\\ GeV}$ and the $\\mathrm{\\chi^{0}}$ has a mass of "\
            "$\\mathrm{200\\ GeV}$), for 2023 "\
            "conditions. The distributions are normalized to unity."
    elif xvar=="ee":
        location = "right"
        table.description = "The ECAL time delay of the $\\mathrm{e/\\gamma}$ L1 seeds in the endcap. The distributions are "\
            "shown for $\\mathrm{Z\\ \\rightarrow\\ ee}$ simulation and $\\mathrm{\\chi^{0}\\ c\\tau}$ values of "\
            "$\\mathrm{3\\ cm,\\ 30\\ cm}$ and $\\mathrm{3\\ m}$, "\
            "assuming the singlet-triplet Higgs dark portal model ($\\mathrm{\\chi^{\\pm}\\ \\rightarrow\\ \\chi^{0} \\ell^{\\pm} \\nu}$, "\
            "where the $\\mathrm{\\chi^{\\pm}}$ has a mass of $\\mathrm{220\\ GeV}$ GeV and the $\\mathrm{\\chi^{0}}$ has a mass of "\
            "$\\mathrm{200\\ GeV}$ GeV), for 2023 "\
            "conditions. The distributions are normalized to unity."
    else:
        raise ValueError("Unexpected input to function makeDelayedDiPhotonHistTable()")
    
    table.location = "Data from Fig. 31 "+location
    table.add_image(f"data_DelayedDiPhoton_SahasransuAR/delayed_dieg10_tdelay_ecal_w_d0_{xvar}.pdf")

    reader = RootFileReader(f"data_DelayedDiPhoton_SahasransuAR/delayed_dieg10_tdelay_ecal_w_d0_{xvar}.root")
    dymc = reader.read_hist_1d(f"genmatched_ph_seedtime_{xvar}_rebinned;1")
    llp3cm = reader.read_hist_1d(f"genmatched_ph_seedtime_{xvar}_rebinned;2")
    llp30cm = reader.read_hist_1d(f"genmatched_ph_seedtime_{xvar}_rebinned;3")
    llp3m = reader.read_hist_1d(f"genmatched_ph_seedtime_{xvar}_rebinned;4")

    xAxisVar = Variable("seed time", is_independent=True, is_binned=True, units="ns")
    xAxisVar.values = dymc["x_edges"]
    table.add_variable(xAxisVar)

    table.add_variable(makeVariable(plot=dymc, label="Z $\\rightarrow$ ee", is_independent=False, is_binned=False, is_symmetric=True, units=""))
    table.add_variable(makeVariable(plot=llp3cm, label="$\\mathrm{\\chi^{\\pm}\\ \\rightarrow\\ \\chi^{0} \\ell^{\\pm} \\nu},\\ c\\tau\\ =\\ $3 cm", is_independent=False, is_binned=False, is_symmetric=True, units=""))
    table.add_variable(makeVariable(plot=llp30cm, label="$\\mathrm{\\chi^{\\pm}\\ \\rightarrow\\ \\chi^{0} \\ell^{\\pm} \\nu},\\ c\\tau\\ =\\ $30 cm", is_independent=False, is_binned=False, is_symmetric=True, units=""))
    table.add_variable(makeVariable(plot=llp3m, label="$\\mathrm{\\chi^{\\pm}\\ \\rightarrow\\ \\chi^{0} \\ell^{\\pm} \\nu},\\ c\\tau\\ =\\ $3 m", is_independent=False, is_binned=False, is_symmetric=True, units=""))

    return table

def makeDelayedDiPhotonDataRateTable():
    table = Table("Delayed Di-Photon HLT rate. with intergated luminosity")

    reader = RootFileReader("data_DelayedDiPhoton_SahasransuAR/ratewintlumi.root")
    table.description = "The HLT rate of the delayed-diphoton trigger for a few representative runs in the first data collected in 2023, "\
        "corresponding to an integrated luminosity of $\\mathrm{4.2\\ fb^{-1}}$, compared with the PU during the same data-taking period , "\
        "as a function of integrated luminosity. The rate decreases nonlinearly during a single fill as a result of the increasing crystal "\
        "opacity. It recovers by the start of the next fill with $\\mathrm{<\\ 1\\%}$ reduction in rate between the fills. The rate generally "\
        "increased throughout the year because of periodic online calibrations to mitigate the loss in trigger efficiency, which was produced "\
        "as a result of the ECAL crystal radiation damage."

    table.location = "Data from Fig. 32 left"
    table.add_image("data_DelayedDiPhoton_SahasransuAR/ratewintlumi.pdf")

    rate = reader.read_graph("rate;1")
    lumi = reader.read_graph("intlumi;1")

    xAxisVar = Variable("Integrated luminosity", is_independent=True, is_binned=False, units="$fb^{-1}$")
    xAxisVar.values = rate["x"]

    table.add_variable(xAxisVar)
    table.add_variable(makeVariable(plot = rate, label = "HLT rate", is_independent=False, is_binned=False, is_symmetric=True, units="Hz"))
    table.add_variable(makeVariable(plot = lumi, label = "PU / 9.04", is_independent=False, is_binned=False, is_symmetric=True, units=""))

    return table

def makeDelayedDiPhotonDataEffTable(xvar):
    table = Table("Delayed Di-Photon L1+HLT eff. with "+xvar)

    if xvar=="seed time ($\mathrm{e_{2}}$)":
        units = "ns"
        location = "Data from Fig. 33"
        data = "tid_elprobe_inZwindow_seedtime_rebinned_clone;1"
        image = "data_DelayedDiPhoton_SahasransuAR/hltdipho10t1ns_eff_seedtime.pdf"
        reader = RootFileReader("data_DelayedDiPhoton_SahasransuAR/hltdipho10t1ns_eff_seedtime.root")
        table.description = "The L1T+HLT efficiency of the delayed-diphoton trigger as a function of the subleading probe electron "\
            "($\\mathrm{e_2}$) supercluster seed time, measured with data collected in 2023. At the HLT, the subleading "\
            "$\\mathrm{e/\\gamma}$ supercluster ($\\mathrm{e/\\gamma_2}$) is required to have $\\mathrm{E_T\\ >\\ 12\\ GeV}$, "\
            "$\\mathrm{|\\eta|\\ <\\ 2.1}$, and a seed time $\\mathrm{>\\ 1\\ ns}$. The trigger is fully efficient above $\\mathrm{1\\ ns}$."

    elif xvar=="$p_{T}$ ($\mathrm{e_{2}}$)":
        units = "GeV"
        location = "Data from Fig. 34 left"
        data = "tid1ns_elprobe_inZwindow_pt_rebinned_clone;1"
        image = "data_DelayedDiPhoton_SahasransuAR/hltdipho10t1ns_eff_pt.pdf"
        reader = RootFileReader("data_DelayedDiPhoton_SahasransuAR/hltdipho10t1ns_eff_pt.root")
        table.description = "The L1T+HLT efficiency of the delayed-diphoton trigger as a function of subleading probe electron "\
        "($\\mathrm{e_2}$) \\mathrm{p_T}, measured with data collected in 2023. At the HLT, the subleading $\\mathrm{e/\\gamma}$ "\
        "supercluster ($\\mathrm{e/\\gamma_2}$) is required to have $\\mathrm{E_T\\ >\\ 12\\ GeV}$, $\\mathrm{|\\eta|\\ <\\ 2.1}$, and a "\
        "seed time $\\mathrm{>\\ 1\\ ns}$. The efficiency rises sharply for $\\mathrm{p_T\\ >\\ 12\\ GeV}$ and plateaus for "\
        "$\\mathrm{p_T\\ >\\ 35\\ GeV}$. The slow rise in between is from additional L1 $\\mathrm{H_T}$ requirements."

    elif xvar=="$\eta$ ($\mathrm{e_{2}}$)":
        units = ""
        location = "Data from Fig. 34 right"
        data = "tid1ns_elprobe_inZwindow_eta_rebinned_clone;1"
        image = "data_DelayedDiPhoton_SahasransuAR/hltdipho10t1ns_eff_eta.pdf"
        reader = RootFileReader("data_DelayedDiPhoton_SahasransuAR/hltdipho10t1ns_eff_eta.root")
        table.description = "The L1T+HLT efficiency of the delayed-diphoton trigger as a function of subleading probe electron "\
        "($\\mathrm{e_2}$) $\\mathrm{\eta}$, measured with data collected in 2023. At the HLT, the subleading $\\mathrm{e/\\gamma}$ "\
        "supercluster ($\\mathrm{e/\\gamma_2}$) is required to have $\\mathrm{E_T\\ >\\ 12\\ GeV}$, $\\mathrm{|\\eta|\\ <\\ 2.1}$, "\
        "and a seed time $\\mathrm{>\\ 1\\ ns}$. The trigger is efficient in the region $\\mathrm{|\\eta|\\ <\\ 2.1}$."
        
    else:
        raise ValueError("Unexpected input to function makeDelayedDiPhotonDataEffTable()")

    table.location = location
    table.add_image(image)

    data = reader.read_teff(data)

    xAxisVar = Variable(xvar, is_independent=True, is_binned=False, units=units)
    xAxisVar.values = data["x"]

    table.add_variable(xAxisVar)
    table.add_variable(makeVariable(plot = data, label = "Data (2023)", is_independent=False, is_binned=False, is_symmetric=False, units=""))

    return table

def extract_histogram_data(hist):
    """
    Extract data from a ROOT histogram including bin centers, values, and uncertainties
    """
    n_bins = hist.GetNbinsX()
    
    # Extract bin centers (x values)
    x_values = []
    x_low = []
    x_high = []
    
    for i in range(1, n_bins + 1):
        bin_center = hist.GetBinCenter(i)
        bin_low = hist.GetBinLowEdge(i)
        bin_high = hist.GetBinLowEdge(i) + hist.GetBinWidth(i)
        
        x_values.append(bin_center)
        x_low.append(bin_low)
        x_high.append(bin_high)
    
    # Extract y values and uncertainties
    y_values = []
    y_errors = []
    
    for i in range(1, n_bins + 1):
        y_val = hist.GetBinContent(i)
        y_err = hist.GetBinError(i)
        
        y_values.append(y_val)
        y_errors.append(y_err)
    
    return {
        'x_centers': x_values,
        'x_low': x_low,
        'x_high': x_high,
        'y_values': y_values,
        'y_errors': y_errors
    }

def create_binned_variable(name, x_low, x_high, units="", is_independent=True):
    """
    Create a binned variable for HEPData
    """
    var = Variable(name, is_independent=is_independent, is_binned=True, units=units)
    
    # Create bin edges from low and high values
    bin_edges = []
    for i in range(len(x_low)):
        bin_edges.append([x_low[i], x_high[i]])
    
    var.values = bin_edges
    return var

def create_dependent_variable(name, y_values, y_errors, units="", uncertainty_label="Statistical uncertainty", CME=13.6):
    """
    Create a dependent variable with uncertainties for HEPData
    """
    var = Variable(name, is_independent=False, is_binned=False, units=units)
    var.values = y_values
    
    # Add statistical uncertainties
    if y_errors and any(err > 0 for err in y_errors):
        unc = Uncertainty(uncertainty_label, is_symmetric=True)
        unc.values = y_errors
        var.add_uncertainty(unc)

    var.add_qualifier("SQRT(S)", CME, "TeV")
    return var

def get_figure_metadata(figure_name):
    """
    Get metadata for each figure based on the paper content
    """
    metadata = {
        "Figure41a": {
            "description": "The L1T+HLT efficiency of the Run 3 (2022, L3) triggers in 2022 data, 2023 data, and simulation as a function of min($p_T$) of the two muons forming TMS-TMS dimuons in events enriched in J/ψ → μμ events. Efficiency in data is the fraction of J/ψ → μμ events recorded by the triggers based on the information from jets and $p_T^{miss}$ that also satisfy the requirements of the Run 3 (2022, L3) triggers. It is compared to the efficiency of the Run 3 (2022, L3) triggers in a combination of simulated samples of J/ψ → μμ events produced in various b hadron decays. The lower panels show the ratio of the data to simulated events.",
            "location": "Data from Figure 41 (upper left)."
        },
        "Figure41b": {
            "description": "The L1T+HLT efficiency of the Run 3 (2022, L3) triggers in 2022 data, 2023 data, and simulation as a function of max($p_T$) of the two muons forming TMS-TMS dimuons in events enriched in J/ψ → μμ events. Efficiency in data is the fraction of J/ψ → μμ events recorded by the triggers based on the information from jets and $p_T^{miss}$ that also satisfy the requirements of the Run 3 (2022, L3) triggers. It is compared to the efficiency of the Run 3 (2022, L3) triggers in a combination of simulated samples of J/ψ → μμ events produced in various b hadron decays. The lower panels show the ratio of the data to simulated events.",
            "location": "Data from Figure 41 (upper right)."
        },
        "Figure41c": {
            "description": "The L1T+HLT efficiency of the Run 3 (2022, L3) triggers in 2022 data, 2023 data, and simulation as a function of min($d_0$) of the two muons forming TMS-TMS dimuons in events enriched in J/ψ → μμ events. Efficiency in data is the fraction of J/ψ → μμ events recorded by the triggers based on the information from jets and $p_T^{miss}$ that also satisfy the requirements of the Run 3 (2022, L3) triggers. It is compared to the efficiency of the Run 3 (2022, L3) triggers in a combination of simulated samples of J/ψ → μμ events produced in various b hadron decays. The lower panels show the ratio of the data to simulated events.",
            "location": "Data from Figure 41 (lower)."
        },
        "Figure42a": {
            "description": "The HLT efficiency, defined as the fraction of events recorded by the Run 2 (2018) triggers that also satisfied the requirements of the Run 3 (2022, L3) triggers, as a function of offline-reconstructed min($d_0$) of the two muons forming TMS-TMS dimuons in events enriched in J/ψ → μμ. The data represent efficiencies during the 2022 and 2023 data-taking periods. For dimuons with offline min($d_0$) > 0.012 cm, the combined efficiency of the L3 muon reconstruction and the online min($d_0$) requirement is larger than 90% in all data-taking periods.",
            "location": "Data from Figure 42 (upper left)."
        },
        "Figure42b": {
            "description": "The HLT efficiency of the Run 3 (2022, L3) triggers and the Run 3 (2022, L3 dTks) triggers for J/ψ → μμ events in the 2022 and 2023 data set as a function of offline-reconstructed min($d_0$) of the two muons forming TMS-TMS dimuons in events enriched in J/ψ → μμ.",
            "location": "Data from Figure 42 (upper right)."
        },
        "Figure42c": {
            "description": "Invariant mass distribution for TMS-TMS dimuons in events recorded by the Run 2 (2018) triggers in the combined 2022 and 2023 data set, and in the subset of events also selected by the Run 3 (2022, L3) trigger and Run 3 (2022, L3 dTks) trigger, illustrating the prompt muon rejection of the L3 triggers.",
            "location": "Data from Figure 42 (lower)."
        },
        "Figure43a": {
            "description": "The HLT efficiency, defined as the fraction of events recorded by the Run 2 (2018) triggers that also satisfied the requirements of the Run 3 (2022, L2) triggers, as a function of offline-reconstructed min($d_0$) of the two muons forming STA-STA dimuons in events enriched in cosmic ray muons. The data represent efficiencies during the 2022 and 2023 data-taking periods. For displaced muons, the efficiency of the online min($d_0$) requirement is larger than 95% in all data-taking periods.",
            "location": "Data from Figure 43 (left)."
        },
        "Figure43b": {
            "description": "The invariant mass distribution for TMS-TMS dimuons in events recorded by the Run 2 (2018) triggers in the combined 2022 and 2023 data set, and in the subset of events also selected by the Run 3 (2022, L2) triggers, illustrating the prompt muon rejection of the Run 3 (2022, L2) triggers.",
            "location": "Data from Figure 43 (right)."
        },
        "Figure40": {
            "description": "The L1T+HLT efficiencies of the various displaced-dimuon triggers and their logical OR as a function of $c\\tau$ for the HAHM signal events with $m_H = 125\ GeV$ and $m_{Z_D} = 20\ GeV$, for 2022 conditions. The efficiency is defined as the fraction of simulated events that satisfy the detector acceptance and the requirements of the following sets of triggers: the Run 2 (2018) triggers (dashed black); the Run 3 (2022, L3) triggers (blue); the Run 3 (2022, L2) triggers (red); and the logical OR of all these triggers (Run 3 (2022), solid black). The lower panel shows the ratio of the overall Run 3 (2022) efficiency to the Run 2 (2018) efficiency.",
            "location": "Data from Figure 40."
        }
    }
    return metadata.get(figure_name, {
        "description": f"PLACEHOLDER: Description for {figure_name}",
        "location": f"PLACEHOLDER: Location for {figure_name}"
    })

def process_single_figure(submission, root_file_path, figure_name):
    """
    Process a single ROOT file and add its data to the submission
    """
    print(f"\n=== Processing {figure_name} ===")
    
    # Open ROOT file and extract histograms
    root_file = ROOT.TFile.Open(root_file_path)
    if not root_file or root_file.IsZombie():
        print(f"Error: Could not open ROOT file {root_file_path}")
        return False
    
    # Get the canvas
    canvas = root_file.Get("c")
    if not canvas:
        print("Error: Could not find canvas 'c' in ROOT file")
        root_file.Close()
        return False
    
    # Extract histograms from canvas
    histograms = collect_hists_from_canvas(canvas)
    
    if not histograms:
        print("Error: No histograms found in canvas")
        root_file.Close()
        return False
    
    print(f"Found {len(histograms)} histograms")
    
    # Get figure metadata
    metadata = get_figure_metadata(figure_name)
    
    # Create a single table for all histograms in the figure
    table = Table(figure_name)
    table.description = metadata["description"]
    table.location = metadata["location"]
    
    # Add keywords
    table.keywords["reactions"] = ["P P --> X"]
    table.keywords["observables"] = ["EFF"]
    table.keywords["phrases"] = ["CMS", "LLP", "long-lived particles", "trigger", "efficiency", "displaced muons"]
    
    # Add figure image if PDF exists and ImageMagick is available
    pdf_path = f"data_Alejandro/{figure_name}.pdf"
    if os.path.exists(pdf_path) and check_imagemagick_available():
        try:
            table.add_image(pdf_path)
            print(f"Added image: {pdf_path}")
        except Exception as e:
            print(f"Warning: Could not add image {pdf_path}: {e}")
    elif os.path.exists(pdf_path):
        print(f"ImageMagick not available - skipping image: {pdf_path}")
    else:
        print(f"Image not found: {pdf_path}")
    
    # Process histograms and filter out duplicates and ratio panels
    processed_names = set()
    unique_histograms = []
    
    for hist in histograms:
        hist_name = hist.GetName()
        y_axis_title = hist.GetYaxis().GetTitle()
        
        # Skip ratio histograms (from ratio panels)
        if "ratio" in hist_name.lower() or "Data/MC" in y_axis_title:
            print(f"Skipping ratio histogram: {hist_name}")
            continue
            
        # Skip duplicate histograms (like _copy versions)
        base_name = hist_name.replace("_copy", "")
        if base_name in processed_names:
            print(f"Skipping duplicate histogram: {hist_name}")
            continue
            
        processed_names.add(base_name)
        unique_histograms.append(hist)
        print(f"Including histogram: {hist_name}")
    
    # Add x-axis variable (same for all histograms)
    if unique_histograms:
        first_hist = unique_histograms[0]
        first_hist_data = extract_histogram_data(first_hist)
        x_axis_title = first_hist.GetXaxis().GetTitle()
        
        # Get proper x-axis name and units
        x_name, x_units = get_x_axis_info(x_axis_title, figure_name)
        
        # Create independent variable (x-axis) - shared by all histograms
        x_var = create_binned_variable(
            name=x_name,
            x_low=first_hist_data['x_low'],
            x_high=first_hist_data['x_high'],
            units=x_units,
            is_independent=True
        )
        table.add_variable(x_var)
    
    # Add each histogram as a dependent variable
    for hist in unique_histograms:
        hist_name = hist.GetName()
        hist_data = extract_histogram_data(hist)
        y_axis_title = hist.GetYaxis().GetTitle()
        
        # Create descriptive variable name based on histogram name and content
        var_name = create_variable_name(hist_name, figure_name)
        
        # Determine units for y-axis
        if "Efficiency" in y_axis_title:
            y_units = ""
        elif "Data/MC" in y_axis_title:
            y_units = ""
        else:
            y_units = ""
        
        # Create dependent variable (y-axis)
        y_var = create_dependent_variable(
            name=var_name,
            y_values=hist_data['y_values'],
            y_errors=hist_data['y_errors'],
            units=y_units,
            uncertainty_label="Statistical uncertainty"
        )
        
        # Add variable to table
        table.add_variable(y_var)
        
        print(f"  - Added {var_name} with {len(hist_data['y_values'])} data points")
    
    # Add table to submission
    submission.add_table(table)
    
    # Close ROOT file
    root_file.Close()
    return True

def get_x_axis_info(x_axis_title, figure_name):
    """
    Get proper x-axis variable name and units based on figure and axis title
    """
    # Clean up the title and extract units
    title = x_axis_title.strip()
    
    # Handle specific figure naming
    if figure_name == "Figure41a":
        return "min($p_T$)", "GeV"
    elif figure_name == "Figure41b":
        return "max($p_T$)", "GeV"
    elif figure_name == "Figure41c":
        return "min($d_0$)", "cm"
    elif figure_name in ["Figure42a", "Figure42b"]:
        return "min($d_0$)", "cm"
    elif figure_name in ["Figure42c", "Figure43b"]:
        return "$m_{\\mu\\mu}$", "GeV"
    elif figure_name == "Figure43a":
        return "min($d_0$)", "cm"
    else:
        # Generic handling - extract units from title
        if "[GeV]" in title:
            clean_title = title.replace("[GeV]", "").strip()
            return clean_title, "GeV"
        elif "[cm]" in title:
            clean_title = title.replace("[cm]", "").strip()
            return clean_title, "cm"
        else:
            return title if title else "Variable", ""

def create_variable_name(hist_name, figure_name):
    """
    Create descriptive variable names based on histogram name and figure
    """
    # Special handling for specific figures with event counts instead of efficiencies
    if figure_name == "Figure42c":
        if "MuonRun3HLTRun2" in hist_name:
            return "Run 2 (2018) observed events"
        elif "DisplacedL3" in hist_name and "dTks" not in hist_name:
            return "Run 3 (2022, L3) observed events"
        elif "dTks" in hist_name:
            return "Run 3 (2022, L3 dTks) observed events"
    elif figure_name == "Figure43b":
        if "MuonRun3HLTRun2" in hist_name:
            return "Run 2 (2018) observed events"
        elif "L3VetoOR" in hist_name:
            return "Run 3 (2022, L2) observed events"
    elif figure_name == "Figure42a":
        # Fix specific naming for Figure42a
        if "HData2022" in hist_name:
            return "Run 3 (2022, L3) trigger efficiency - 2022 data"
        elif "2023" in hist_name:
            return "Run 3 (2022, L3) trigger efficiency - 2023 data"
    
    # Handle different histogram types based on naming patterns (for efficiency plots)
    if "dTks" in hist_name:
        return "Run 3 (2022, L3 dTks) trigger efficiency"
    elif "DisplacedL3" in hist_name and "Muon" in hist_name:
        return "Run 3 (2022, L3) trigger efficiency"
    elif "DisplacedL3" in hist_name and "JetMET" in hist_name:
        if "2022" in hist_name:
            return "Run 3 (2022, L3) trigger efficiency - 2022 data"
        elif "2023" in hist_name:
            return "Run 3 (2022, L3) trigger efficiency - 2023 data"
        else:
            return "Run 3 (2022, L3) trigger efficiency"
    elif "BtoJPsi" in hist_name:
        return "Run 3 (2022, L3) trigger efficiency - simulation"
    elif "COSMI" in hist_name:
        if "2022" in hist_name:
            return "Run 3 (2022, L2) trigger efficiency - 2022 data"
        elif "2023" in hist_name:
            return "Run 3 (2022, L2) trigger efficiency - 2023 data"
        else:
            return "Run 3 (2022, L2) trigger efficiency"
    elif "ratio" in hist_name:
        return "Data/MC ratio"
    else:
        # Generic fallback
        return f"Efficiency ({hist_name})"

def process_existing_yaml_file(submission, yaml_file_path, figure_name):
    """
    Process an existing YAML file and add it to the submission with proper metadata
    """
    print(f"\n=== Processing existing YAML: {figure_name} ===")
    
    if not os.path.exists(yaml_file_path):
        print(f"Error: YAML file not found: {yaml_file_path}")
        return False
    
    try:
        # Read the existing YAML file
        with open(yaml_file_path, 'r') as f:
            yaml_content = yaml.safe_load(f)
        
        # Get figure metadata
        metadata = get_figure_metadata(figure_name)
        
        # Create a new table with proper metadata
        table = Table(figure_name)
        table.description = metadata["description"]
        table.location = metadata["location"]
        
        # Add keywords
        table.keywords["reactions"] = ["P P --> X"]
        table.keywords["observables"] = ["EFF"]
        table.keywords["phrases"] = ["CMS", "LLP", "long-lived particles", "trigger", "efficiency", "displaced muons", "proper decay length"]
        
        # Add figure image if PDF exists and ImageMagick is available
        pdf_source_path = f"data_Alejandro/fromDisplacedDimuons/{figure_name}.pdf"
        if os.path.exists(pdf_source_path) and check_imagemagick_available():
            try:
                # Use relative path to the PDF in fromDisplacedDimuons directory
                table.add_image(pdf_source_path)
                print(f"Added image: {pdf_source_path}")
            except Exception as e:
                print(f"Warning: Could not add image {pdf_source_path}: {e}")
        elif os.path.exists(pdf_source_path):
            print(f"ImageMagick not available - skipping image: {pdf_source_path}")
        else:
            print(f"Image not found: {pdf_source_path}")
        
        # Extract and add independent variables
        if 'independent_variables' in yaml_content:
            for indep_var in yaml_content['independent_variables']:
                var_name = indep_var['header']['name']
                var_units = indep_var['header'].get('units', '')
                var_values = indep_var['values']
                
                # Create Variable object
                var = Variable(var_name, is_independent=True, is_binned=False, units=var_units)
                var.values = [v['value'] for v in var_values]
                table.add_variable(var)
                print(f"  - Added independent variable: {var_name} with {len(var.values)} points")
        
        # Extract and add dependent variables
        if 'dependent_variables' in yaml_content:
            for dep_var in yaml_content['dependent_variables']:
                var_name = dep_var['header']['name']
                var_values = dep_var['values']
                qualifiers = dep_var.get('qualifiers', [])
                
                # Create Variable object
                var = Variable(var_name, is_independent=False, is_binned=False, units="")
                var.values = [v['value'] for v in var_values]
                
                # Add qualifiers
                for qualifier in qualifiers:
                    var.add_qualifier(qualifier['name'], qualifier['value'])
                
                table.add_variable(var)
                print(f"  - Added dependent variable: {var_name} with {len(var.values)} points")
        
        # Add table to submission
        submission.add_table(table)
        return True
        
    except Exception as e:
        print(f"Error processing YAML file {yaml_file_path}: {e}")
        return False


def makeDoubleDispL3MuonSigEffTable():
    table = Table("Double displaced L3 muon signal eff vs min($\mathrm{p_{T}}$)")
    table.description = "The L1T+HLT efficiency of the double displaced L3 muon trigger as a function of min($\mathrm{p_{T}}$) of the two global or tracker muons in the event. The efficiency is plotted for HAHM signal events for 2022 conditions with $m_{Z_D} = 50$ GeV and $\epsilon = 4 \\times 10^{-9}$ (black triangles), $m_{Z_D} = 60$ GeV and $\epsilon = 2 \\times 10^{-9}$ (red triangles), and $m_H=125$ GeV in both cases. The events are required to have at least two good global or tracker muons with $\mathrm{p_T}>23$ GeV."
    table.location = "Data from Fig. 45"
    table.add_image("data_Juliette/pat_2022_minpt_REP_PRESEL_PT23_add_HLTDoubleMu43.pdf")

    reader = RootFileReader("data_Juliette/DoubleDispL3MuonSigEff.root")
    g_125_50_4 = reader.read_teff("HHTo2ZdTo2Mu2X_125_50_4e-09preHLTDoubleMu43_clone;1")
    g_125_60_2 = reader.read_teff("HHTo2ZdTo2Mu2X_125_60_2e-09preHLTDoubleMu43_clone;1")

    minpT = Variable("min($\mathrm{p_{T}}$)", is_independent=True, is_binned=False, units="GeV")
    minpT.values = g_125_50_4["x"]

    ### add variables and add table to submission
    table.add_variable(minpT)
    table.add_variable(makeVariable(plot = g_125_50_4, label = "$\mathrm{H} \\to 2\mathrm{Z_D} \\to 2\\mu 2\mathrm{X}$ (125, 50, 4e-09)", is_independent=False, is_binned=False, is_symmetric=False, units=""))
    table.add_variable(makeVariable(plot = g_125_60_2, label = "$\mathrm{H} \\to 2\mathrm{Z_D} \\to 2\\mu 2\mathrm{X}$ (125, 60, 2e-09)", is_independent=False, is_binned=False, is_symmetric=False, units=""))

    return table

def makeDoubleDispL3MuonDataMCEffTable(xvar):
    table = Table("Double disp. L3mu data&bkg eff vs "+xvar)

    if(xvar=="min($\mathrm{d_{0}}$)"):
        units = "cm"
        location = "left"
        image = "data_Juliette/pat_2022_mind0pv_REP_PT45_JPSIMASS_add_HLTDoubleMu43_Jpsi_eff.pdf"
        reader = RootFileReader("data_Juliette/DoubleDispL3MuonDataMCEff_mind0.root")
        table.description = "The L1T+HLT efficiency of the double displaced L3 muon trigger in 2022, as a function of "+xvar+" of the two global or tracker muons in the event. The efficiency is plotted for MC-simulated $J/\\psi \to \\mu\\mu$ events produced in various b hadron decays (green squares) and data enriched in $J/\\psi \to \\mu\\mu$  events recorded by jet- and $\mathrm{p_T^miss}$-based triggers (black points). The events are required to have at least two good global or tracker muons compatible with the $J/\\psi$ meson mass and with $\mathrm{p_T}>45$ GeV."
    elif(xvar=="min($\mathrm{p_{T}}$)"):
        units = "GeV"
        location = "right"
        image = "data_Juliette/pat_2022_minpt_REP_JPSIMASS_PT23_add_HLTDoubleMu43_Jpsi_eff.pdf"
        reader = RootFileReader("data_Juliette/DoubleDispL3MuonDataMCEff_minpT.root")
        table.description = "The L1T+HLT efficiency of the double displaced L3 muon trigger in 2022, as a function of "+xvar+" of the two global or tracker muons in the event. The efficiency is plotted for MC-simulated $J/\\psi \to \\mu\\mu$ events produced in various b hadron decays (green squares) and data enriched in $J/\\psi \to \\mu\\mu$  events recorded by jet- and $\mathrm{p_T^miss}$-based triggers (black points). The events are required to have at least two good global or tracker muons compatible with the $J/\\psi$ meson mass and with $\mathrm{p_T}>23$ GeV."

    table.location = "Data from Fig. 46 "+location
    table.add_image(image)

    MC = reader.read_teff("HBtoJPsipreHLTDoubleMu43_clone;1")
    data = reader.read_teff("HJetMETData2022preHLTDoubleMu43_clone;1")

    xAxisVar = Variable(xvar, is_independent=True, is_binned=False, units=units)
    xAxisVar.values = MC["x"]

    ### add variables and add table to submission
    table.add_variable(xAxisVar)
    table.add_variable(makeVariable(plot = MC, label = "Nonprompt $J/\\psi \\to \\mu\\mu$", is_independent=False, is_binned=False, is_symmetric=False, units=""))
    table.add_variable(makeVariable(plot = data, label = "Data (2022)", is_independent=False, is_binned=False, is_symmetric=False, units=""))

    return table

def makeMuonNoBPTXRateVsNBunchesTable(year):
    if(year=="2016" or year=="2017" or year=="2018"):
        CME="13"
    elif(year=="2022" or year=="2023" or year=="2024"):
        CME="13.6"
    table = Table("Muon NoBPTX HLT rate vs number of colliding bunches ("+year+")")
    table.description = "Rate of the main muon No-BPTX HLT path as a function of the number of colliding bunches, for "+year+"."
    table.location = "Data from Fig. 58"
    table.add_image("data_Juliette/NoBPTXL2Mu40_RateVsNCollidingBunches.pdf")

    reader = RootFileReader("data_Juliette/juliette.root")
    g = reader.read_graph("g_"+year+";1")

    nBunches = Variable("Number of colliding bunches", is_independent=True, is_binned=False, units="")
    nBunches.values = g["x"]

    ### add variables and add table to submission
    table.add_variable(nBunches)
    table.add_variable(makeVariable(plot = g, label = "HLT rate in "+year, is_independent=False, is_binned=False, is_symmetric=True, units="Hz", CME=CME))

    return table

def main():
    # Check if ImageMagick is available for image processing
    has_imagemagick = check_imagemagick_available()
    if has_imagemagick:
        print("✓ ImageMagick available - images will be processed")
    else:
        print("⚠ ImageMagick not available - skipping image processing")
    
    # Create the submission object
    submission = Submission()
    
    # Add general submission metadata
    #submission.comment = "Strategy and performance of CMS long-lived particle triggers in proton-proton collisions at sqrt(s) = 13.6 TeV. This submission contains trigger efficiency measurements for displaced muon triggers during CMS Run 3 (2022-2024)."

    submission.read_abstract("data_Juliette/abstract.txt")
    #submission.add_link("Webpage with all figures and tables", "https://cms-results.web.cern.ch/cms-results/public-results/publications/EXO-23-016/")
    #submission.add_link("arXiv", "http://arxiv.org/abs/arXiv:")
    #submission.add_record_id(1940976, "inspire")

    # Create output directory early
    output_dir = "hepdata_output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    successful_figures = 0

    # Figure 21
    submission.add_table(makeHcalTowerEffTable())

    # Figure 22
    submission.add_table(makeHcalLLPflaggedJetEffTable())

    # Figure 23
    submission.add_table(makeHcalL1JetHTEffTable("HT"))
    submission.add_table(makeHcalL1JetHTEffTable("jet"))

    # Figure 24
    submission.add_table(makeHcalL1DecayREffTable())

    # Figure 31
    submission.add_table(makeDelayedDiPhotonHistTable("eb"))
    submission.add_table(makeDelayedDiPhotonHistTable("ee"))

    # Figure 32
    submission.add_table(makeDelayedDiPhotonDataRateTable())

    # Figure 33
    submission.add_table(makeDelayedDiPhotonDataEffTable("seed time ($\mathrm{e_{2}}$)"))
    
    # Figure 34
    submission.add_table(makeDelayedDiPhotonDataEffTable("$p_{T}$ ($\mathrm{e_{2}}$)"))
    submission.add_table(makeDelayedDiPhotonDataEffTable("$\eta$ ($\mathrm{e_{2}}$)"))

    #Figure 39
    submission.add_table(makeDisplacedMuonL1EffTable("BMTF"))
    submission.add_table(makeDisplacedMuonL1EffTable("OMTF"))
    submission.add_table(makeDisplacedMuonL1EffTable("EMTF"))
    
    # Process existing YAML files from fromDisplacedDimuons directory FIRST (for Figure 40)
    yaml_dir = "data_Alejandro/fromDisplacedDimuons"
    if os.path.exists(yaml_dir):
        yaml_files = [f for f in os.listdir(yaml_dir) if f.endswith('.yaml')]
        yaml_files.sort()  # Process in alphabetical order
        for yaml_file in yaml_files:
            figure_name = yaml_file.replace('.yaml', '')
            yaml_file_path = os.path.join(yaml_dir, yaml_file)
            
            if process_existing_yaml_file(submission, yaml_file_path, figure_name):
                successful_figures += 1
            else:
                print(f"Failed to process existing YAML {figure_name}")
    
    # Process ROOT files (Figures 41-43)
    data_dir = "data_Alejandro"
    root_files = [f for f in os.listdir(data_dir) if f.endswith('.root')]
    root_files.sort()  # Process in alphabetical order
    
    for root_file in root_files:
        figure_name = root_file.replace('.root', '')
        root_file_path = os.path.join(data_dir, root_file)
        
        if process_single_figure(submission, root_file_path, figure_name):
            successful_figures += 1
        else:
            print(f"Failed to process {figure_name}")

    print(f"\nSuccessfully processed {successful_figures} figures")

    #Figure 45
    submission.add_table(makeDoubleDispL3MuonSigEffTable())

    #Figure 46
    submission.add_table(makeDoubleDispL3MuonDataMCEffTable("min($\mathrm{d_{0}}$)"))
    submission.add_table(makeDoubleDispL3MuonDataMCEffTable("min($\mathrm{p_{T}}$)"))

    #Figure 58
    submission.add_table(makeMuonNoBPTXRateVsNBunchesTable("2016"))
    submission.add_table(makeMuonNoBPTXRateVsNBunchesTable("2017"))
    submission.add_table(makeMuonNoBPTXRateVsNBunchesTable("2018"))
    submission.add_table(makeMuonNoBPTXRateVsNBunchesTable("2022"))
    submission.add_table(makeMuonNoBPTXRateVsNBunchesTable("2023"))
    submission.add_table(makeMuonNoBPTXRateVsNBunchesTable("2024"))

    for table in submission.tables:
        table.keywords["cmenergies"] = [13000,13600]
    
    # Generate HEPData files
    try:
        submission.create_files(output_dir)
        print(f"\nHEPData files created in '{output_dir}' directory")
    except Exception as e:
        print(f"Error creating HEPData files: {e}")
        if "ImageMagick" in str(e) or "convert" in str(e) or "does not exist" in str(e):
            print("This appears to be an ImageMagick-related error.")
            print("Attempting to create submission without images...")
            
            # Remove all images from tables and try again
            for table in submission.tables:
                if hasattr(table, 'image_files'):
                    table.image_files = []

            try:
                submission.create_files(output_dir)
                print(f"\nHEPData files created in '{output_dir}' directory (without images)")
            except Exception as e2:
                print(f"Failed to create submission even without images: {e2}")
                raise
        else:
            raise
    print("Files generated:")
    for file in sorted(os.listdir(output_dir)):
        print(f"  - {file}")
    
    # Create tar.gz archive (hepdata_lib creates submission.tar.gz automatically)
    
    print(f"\nProcessing complete! Generated HEPData submission with {successful_figures} figures.")
    print("\nSubmission includes:")
    print("  - Trigger efficiency measurements from CMS Run 3 (2022-2024)")
    print("  - Figures 40, 41a-c, 42a-c, and 43a-b from EXO-23-016")
    print("  - Complete metadata and figure descriptions from the paper")
    print("  - Statistical uncertainties for all measurements")
    print("  - Proper decay length (cτ) dependence studies for displaced dimuons")


    #submission.add_additional_resource("Signal generation", "data_Juliette/signalGeneration.tar.gz", copy_file=True)                                                                            
    #submission.create_files("hepdataRecord",remove_old=True)
    
    
if __name__ == "__main__":
    main()
