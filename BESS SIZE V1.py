import pandas as pd
import numpy as np
import math
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
import json
from fpdf import FPDF
import matplotlib.pyplot as plt
from datetime import datetime
from enum import Enum
import random

# ==================== ENUMS AND DATA STRUCTURES ====================

class ProjectApplication(Enum):
    SELF_CONSUMPTION = "Self Consumption Power Supply"
    FREQUENCY_REGULATION = "Frequency Regulation"
    PEAK_SHAVING = "Peak Shaving"
    BLACK_START = "Black Start"
    RENEWABLE_INTEGRATION = "Renewable Integration"
    MICROGRID = "Microgrid"
    BACKUP_POWER = "Backup Power"

class AmbientEnvironment(Enum):
    INLAND = "Inland"
    COASTAL = "Coastal"
    DESERT = "Desert"
    ARCTIC = "Arctic"
    INDUSTRIAL = "Industrial"

class CoolingSystem(Enum):
    LIQUID = "Liquid Cooling System"
    AIR = "Air Cooling System"
    PHASE_CHANGE = "Phase Change Material"
    IMMERSION = "Immersion Cooling"

class GridStability(Enum):
    STABLE = "Stable"
    UNSTABLE = "Unstable"
    WEAK = "Weak Grid"
    ISLANDED = "Islanded"

class TransformerType(Enum):
    DRY = "Dry-Type"
    OIL = "Oil-Filled"
    CAST_RESIN = "Cast Resin"
    BIODEGRADABLE = "Biodegradable Oil"

class PCSMode(Enum):
    GRID_FORMING = "Grid-Forming"
    GRID_FOLLOWING = "Grid-Following"

class MountingType(Enum):
    PAD = "Pad Mounted"
    POLE = "Pole Mounted"
    INDOOR = "Indoor"
    CONTAINERIZED = "Containerized"

# ==================== DATABASE DEFINITIONS ====================

# Enhanced Battery Models Database with more details
BATTERY_MODELS = {
    "BESS-1000": {"capacity_kwh": 1000, "cost_per_kwh": 450, "weight_kg": 8000, 
                  "dimensions": "2.4x1.2x2.3m", "chemistry": "LFP", "cycle_life": 6000,
                  "warranty_years": 10, "operating_temp": "-20°C to 60°C"},
    "BESS-2000": {"capacity_kwh": 2000, "cost_per_kwh": 430, "weight_kg": 15000, 
                  "dimensions": "2.4x2.4x2.3m", "chemistry": "LFP", "cycle_life": 6000,
                  "warranty_years": 10, "operating_temp": "-20°C to 60°C"},
    "BESS-3000": {"capacity_kwh": 3000, "cost_per_kwh": 420, "weight_kg": 22000, 
                  "dimensions": "6.0x1.2x2.3m", "chemistry": "LFP", "cycle_life": 6000,
                  "warranty_years": 10, "operating_temp": "-20°C to 60°C"},
    "BESS-3727": {"capacity_kwh": 3727.36, "cost_per_kwh": 410, "weight_kg": 27000, 
                  "dimensions": "6.0x1.5x2.3m", "chemistry": "NMC", "cycle_life": 5000,
                  "warranty_years": 10, "operating_temp": "-20°C to 60°C"},
    "BESS-4000": {"capacity_kwh": 4000, "cost_per_kwh": 405, "weight_kg": 29000, 
                  "dimensions": "6.0x1.6x2.3m", "chemistry": "NMC", "cycle_life": 5000,
                  "warranty_years": 10, "operating_temp": "-20°C to 60°C"},
    "BESS-5016": {"capacity_kwh": 5015.9, "cost_per_kwh": 400, "weight_kg": 36000, 
                  "dimensions": "6.0x2.0x2.3m", "chemistry": "NMC", "cycle_life": 5000,
                  "warranty_years": 10, "operating_temp": "-20°C to 60°C"},
    "BESS-6000": {"capacity_kwh": 6000, "cost_per_kwh": 395, "weight_kg": 42000, 
                  "dimensions": "6.0x2.4x2.3m", "chemistry": "NMC", "cycle_life": 5000,
                  "warranty_years": 10, "operating_temp": "-20°C to 60°C"},
    "BESS-7000": {"capacity_kwh": 7000, "cost_per_kwh": 390, "weight_kg": 48000, 
                  "dimensions": "6.0x2.8x2.3m", "chemistry": "NMC", "cycle_life": 5000,
                  "warranty_years": 10, "operating_temp": "-20°C to 60°C"},
    "BESS-8000": {"capacity_kwh": 8000, "cost_per_kwh": 385, "weight_kg": 54000, 
                  "dimensions": "6.0x3.2x2.3m", "chemistry": "NMC", "cycle_life": 5000,
                  "warranty_years": 10, "operating_temp": "-20°C to 60°C"},
    "BESS-9000": {"capacity_kwh": 9000, "cost_per_kwh": 380, "weight_kg": 60000, 
                  "dimensions": "12.0x2.4x2.3m", "chemistry": "NMC", "cycle_life": 5000,
                  "warranty_years": 10, "operating_temp": "-20°C to 60°C"},
    "BESS-10000": {"capacity_kwh": 10000, "cost_per_kwh": 375, "weight_kg": 66000, 
                   "dimensions": "12.0x2.4x2.3m", "chemistry": "NMC", "cycle_life": 5000,
                   "warranty_years": 10, "operating_temp": "-20°C to 60°C"},
    "BESS-12000": {"capacity_kwh": 12000, "cost_per_kwh": 370, "weight_kg": 78000, 
                   "dimensions": "12.0x2.9x2.3m", "chemistry": "NMC", "cycle_life": 5000,
                   "warranty_years": 10, "operating_temp": "-20°C to 60°C"},
    "BESS-15000": {"capacity_kwh": 15000, "cost_per_kwh": 365, "weight_kg": 96000, 
                   "dimensions": "12.0x3.6x2.3m", "chemistry": "NMC", "cycle_life": 5000,
                   "warranty_years": 10, "operating_temp": "-20°C to 60°C"},
    "BESS-20000": {"capacity_kwh": 20000, "cost_per_kwh": 360, "weight_kg": 126000, 
                   "dimensions": "12.0x4.8x2.3m", "chemistry": "NMC", "cycle_life": 5000,
                   "warranty_years": 10, "operating_temp": "-20°C to 60°C"},
}

# Enhanced PCS Models Database
PCS_MODELS = {
    "PCS-1.25MW": {"power_mw": 1.25, "cost": 125000, "efficiency": 0.98, "voltage_kv": 0.69,
                   "dimensions": "1.2x0.8x2.0m", "weight_kg": 1200, "cooling": "Air"},
    "PCS-1.5MW": {"power_mw": 1.5, "cost": 140000, "efficiency": 0.98, "voltage_kv": 0.69,
                  "dimensions": "1.2x0.8x2.0m", "weight_kg": 1300, "cooling": "Air"},
    "PCS-1.75MW": {"power_mw": 1.75, "cost": 155000, "efficiency": 0.98, "voltage_kv": 0.69,
                   "dimensions": "1.5x0.9x2.0m", "weight_kg": 1500, "cooling": "Air"},
    "PCS-2MW": {"power_mw": 2.0, "cost": 170000, "efficiency": 0.98, "voltage_kv": 0.69,
                "dimensions": "1.5x0.9x2.0m", "weight_kg": 1600, "cooling": "Air"},
    "PCS-2.5MW": {"power_mw": 2.5, "cost": 200000, "efficiency": 0.98, "voltage_kv": 0.69,
                  "dimensions": "1.8x1.0x2.2m", "weight_kg": 1800, "cooling": "Liquid"},
    "PCS-3MW": {"power_mw": 3.0, "cost": 230000, "efficiency": 0.98, "voltage_kv": 0.69,
                "dimensions": "1.8x1.0x2.2m", "weight_kg": 2000, "cooling": "Liquid"},
    "PCS-3.5MW": {"power_mw": 3.5, "cost": 260000, "efficiency": 0.98, "voltage_kv": 0.69,
                  "dimensions": "2.0x1.2x2.2m", "weight_kg": 2200, "cooling": "Liquid"},
    "PCS-4MW": {"power_mw": 4.0, "cost": 290000, "efficiency": 0.98, "voltage_kv": 0.69,
                "dimensions": "2.0x1.2x2.2m", "weight_kg": 2400, "cooling": "Liquid"},
    "PCS-5MW": {"power_mw": 5.0, "cost": 350000, "efficiency": 0.98, "voltage_kv": 0.69,
                "dimensions": "2.4x1.4x2.2m", "weight_kg": 2800, "cooling": "Liquid"},
    "PCS-6MW": {"power_mw": 6.0, "cost": 410000, "efficiency": 0.98, "voltage_kv": 0.69,
                "dimensions": "2.4x1.4x2.2m", "weight_kg": 3200, "cooling": "Liquid"},
    "PCS-7MW": {"power_mw": 7.0, "cost": 470000, "efficiency": 0.98, "voltage_kv": 0.69,
                "dimensions": "2.8x1.6x2.2m", "weight_kg": 3600, "cooling": "Liquid"},
    "PCS-8MW": {"power_mw": 8.0, "cost": 530000, "efficiency": 0.98, "voltage_kv": 0.69,
                "dimensions": "2.8x1.6x2.2m", "weight_kg": 4000, "cooling": "Liquid"},
    "PCS-10MW": {"power_mw": 10.0, "cost": 650000, "efficiency": 0.98, "voltage_kv": 0.69,
                 "dimensions": "3.2x1.8x2.2m", "weight_kg": 4800, "cooling": "Liquid"},
}

# Enhanced Transformer Models Database
TRANSFORMER_MODELS = {
    "TX-1.25MVA": {"power_mva": 1.25, "cost": 45000, "type": TransformerType.DRY,
                   "dimensions": "1.5x1.0x1.8m", "weight_kg": 1800, "losses": 1.2,
                   "impedance": 6.0, "mounting": MountingType.PAD},
    "TX-1.5MVA": {"power_mva": 1.5, "cost": 52000, "type": TransformerType.DRY,
                  "dimensions": "1.6x1.1x1.8m", "weight_kg": 2000, "losses": 1.3,
                  "impedance": 6.0, "mounting": MountingType.PAD},
    "TX-1.75MVA": {"power_mva": 1.75, "cost": 59000, "type": TransformerType.DRY,
                   "dimensions": "1.7x1.2x1.8m", "weight_kg": 2200, "losses": 1.4,
                   "impedance": 6.0, "mounting": MountingType.PAD},
    "TX-2MVA": {"power_mva": 2.0, "cost": 65000, "type": TransformerType.DRY,
                "dimensions": "1.8x1.3x1.8m", "weight_kg": 2400, "losses": 1.5,
                "impedance": 6.0, "mounting": MountingType.PAD},
    "TX-2.5MVA": {"power_mva": 2.5, "cost": 75000, "type": TransformerType.DRY,
                  "dimensions": "2.0x1.4x1.8m", "weight_kg": 2800, "losses": 1.6,
                  "impedance": 6.0, "mounting": MountingType.PAD},
    "TX-3MVA": {"power_mva": 3.0, "cost": 85000, "type": TransformerType.DRY,
                "dimensions": "2.2x1.5x1.8m", "weight_kg": 3200, "losses": 1.7,
                "impedance": 6.0, "mounting": MountingType.PAD},
    "TX-3.5MVA": {"power_mva": 3.5, "cost": 95000, "type": TransformerType.DRY,
                  "dimensions": "2.4x1.6x1.8m", "weight_kg": 3600, "losses": 1.8,
                  "impedance": 6.0, "mounting": MountingType.PAD},
    "TX-4MVA": {"power_mva": 4.0, "cost": 105000, "type": TransformerType.DRY,
                "dimensions": "2.6x1.7x1.8m", "weight_kg": 4000, "losses": 1.9,
                "impedance": 6.0, "mounting": MountingType.PAD},
    "TX-5MVA": {"power_mva": 5.0, "cost": 125000, "type": TransformerType.DRY,
                "dimensions": "2.8x1.8x1.8m", "weight_kg": 4500, "losses": 2.0,
                "impedance": 6.0, "mounting": MountingType.PAD},
    "TX-6MVA": {"power_mva": 6.0, "cost": 145000, "type": TransformerType.OIL,
                "dimensions": "3.0x2.0x2.0m", "weight_kg": 5000, "losses": 2.1,
                "impedance": 6.5, "mounting": MountingType.PAD},
    "TX-7MVA": {"power_mva": 7.0, "cost": 165000, "type": TransformerType.OIL,
                "dimensions": "3.2x2.2x2.0m", "weight_kg": 5500, "losses": 2.2,
                "impedance": 6.5, "mounting": MountingType.PAD},
    "TX-8MVA": {"power_mva": 8.0, "cost": 185000, "type": TransformerType.OIL,
                "dimensions": "3.4x2.4x2.0m", "weight_kg": 6000, "losses": 2.3,
                "impedance": 6.5, "mounting": MountingType.PAD},
    "TX-10MVA": {"power_mva": 10.0, "cost": 220000, "type": TransformerType.OIL,
                 "dimensions": "3.6x2.6x2.0m", "weight_kg": 7000, "losses": 2.5,
                 "impedance": 6.5, "mounting": MountingType.PAD},
    "TX-12MVA": {"power_mva": 12.0, "cost": 250000, "type": TransformerType.OIL,
                 "dimensions": "3.8x2.8x2.0m", "weight_kg": 8000, "losses": 2.7,
                 "impedance": 6.5, "mounting": MountingType.PAD},
    "TX-15MVA": {"power_mva": 15.0, "cost": 300000, "type": TransformerType.OIL,
                 "dimensions": "4.0x3.0x2.2m", "weight_kg": 9500, "losses": 3.0,
                 "impedance": 6.5, "mounting": MountingType.PAD},
}

# Enhanced Switchgear/RMU Database
SWITCHGEAR_MODELS = {
    "SG-0.4kV-ACB": {"voltage_kv": 0.4, "cost": 15000, "type": "ACB", "current_rating": 4000,
                     "breaking_capacity": 65, "dimensions": "0.8x0.6x2.2m", "weight_kg": 600},
    "SG-0.69kV-ACB": {"voltage_kv": 0.69, "cost": 18000, "type": "ACB", "current_rating": 3200,
                      "breaking_capacity": 65, "dimensions": "0.8x0.6x2.2m", "weight_kg": 650},
    "SG-11kV-RMU": {"voltage_kv": 11, "cost": 35000, "type": "RMU", "current_rating": 630,
                    "breaking_capacity": 25, "dimensions": "1.5x1.0x2.0m", "weight_kg": 1200},
    "SG-33kV-RMU": {"voltage_kv": 33, "cost": 75000, "type": "RMU", "current_rating": 630,
                    "breaking_capacity": 25, "dimensions": "2.0x1.2x2.5m", "weight_kg": 2000},
    "SG-132kV-GIS": {"voltage_kv": 132, "cost": 250000, "type": "GIS", "current_rating": 2000,
                     "breaking_capacity": 40, "dimensions": "4.0x3.0x4.0m", "weight_kg": 8000},
}

# Enhanced AC System Cabinet Database
AC_CABINET_MODELS = {
    "AC-CAB-S": {"size": "Small", "cost": 10000, "capacity_units": 2,
                 "dimensions": "2.0x1.0x2.2m", "weight_kg": 800},
    "AC-CAB-M": {"size": "Medium", "cost": 15000, "capacity_units": 4,
                 "dimensions": "3.0x1.2x2.2m", "weight_kg": 1200},
    "AC-CAB-L": {"size": "Large", "cost": 20000, "capacity_units": 6,
                 "dimensions": "4.0x1.4x2.2m", "weight_kg": 1600},
}

# Enhanced EMS & SCADA Database
EMS_SCADA_SYSTEMS = {
    "EMS-BASIC": {"type": "Basic", "cost": 50000, "features": "Monitoring, Basic Control",
                  "hardware": "Industrial PC", "software": "Web-based Interface",
                  "compatibility": "Modbus TCP/IP, DNP3"},
    "EMS-ADV": {"type": "Advanced", "cost": 100000, "features": "Monitoring, Control, Forecasting",
                "hardware": "Redundant Servers", "software": "Advanced Analytics",
                "compatibility": "Modbus TCP/IP, DNP3, IEC 61850"},
    "EMS-PRO": {"type": "Professional", "cost": 200000, "features": "Full SCADA, AI Forecasting, Grid Services",
                "hardware": "High Availability Cluster", "software": "AI-Powered Platform",
                "compatibility": "Modbus TCP/IP, DNP3, IEC 61850, OPC UA"},
}

# Enhanced Containerization Options
CONTAINER_OPTIONS = {
    "CONT-20FT": {"size": "20ft", "cost": 25000, "capacity_kwh": 4000,
                  "dimensions": "6.1x2.4x2.6m", "weight_kg": 3000,
                  "insulation": "Standard", "cooling": "Air Conditioning"},
    "CONT-40FT": {"size": "40ft", "cost": 40000, "capacity_kwh": 8000,
                  "dimensions": "12.2x2.4x2.6m", "weight_kg": 5000,
                  "insulation": "Enhanced", "cooling": "Air Conditioning"},
    "CONT-40FT-HC": {"size": "40ft High Cube", "cost": 45000, "capacity_kwh": 10000,
                     "dimensions": "12.2x2.4x2.9m", "weight_kg": 5500,
                     "insulation": "Enhanced", "cooling": "Air Conditioning"},
    "CONT-CUSTOM": {"size": "Custom", "cost": 60000, "capacity_kwh": 15000,
                    "dimensions": "Custom", "weight_kg": 7000,
                    "insulation": "Premium", "cooling": "Liquid Cooling"},
}

# Cabling and Accessories Database
CABLING_OPTIONS = {
    "CAB-LV": {"type": "Low Voltage", "cost_per_m": 150, "current_rating": 400,
               "voltage_rating": 1, "insulation": "XLPE"},
    "CAB-MV": {"type": "Medium Voltage", "cost_per_m": 300, "current_rating": 630,
               "voltage_rating": 36, "insulation": "XLPE"},
    "CAB-HV": {"type": "High Voltage", "cost_per_m": 600, "current_rating": 1200,
               "voltage_rating": 132, "insulation": "XLPE"},
}

# Fire Protection Systems
FIRE_PROTECTION_SYSTEMS = {
    "FIRE-AFSS": {"type": "Aerosol Fire Suppression", "cost": 20000, "coverage": "100m²",
                  "standards": "NFPA, UL"},
    "FIRE-FM200": {"type": "FM-200 Gas System", "cost": 35000, "coverage": "200m²",
                   "standards": "NFPA, UL"},
    "FIRE-WATER": {"type": "Water Mist System", "cost": 25000, "coverage": "150m²",
                   "standards": "NFPA, UL"},
}

# ==================== MAIN CALCULATION CLASS ====================

@dataclass
class BESSSizingInput:
    """Class to hold BESS sizing input parameters"""
    customer_load_mw: float
    discharge_duration_hr: float
    c_rate: float
    grid_power_mw: float
    solar_power_mw: float
    other_power_mw: float
    project_application: ProjectApplication
    ambient_environment: AmbientEnvironment
    voltage_standard_kv: float
    grid_stability: GridStability
    cooling_system: CoolingSystem
    cycles_per_day: int
    black_start_required: bool
    dod_percent: float = 90.0
    static_efficiency_percent: float = 90.0
    cycle_efficiency_percent: float = 95.0
    power_factor: float = 0.95
    aging_derate_percent: float = 5.0
    temperature_derate_percent: float = 3.0
    auxiliary_load_percent: float = 2.0
    charging_c_rate: Optional[float] = None
    cable_length_m: float = 50.0
    site_prep_cost: float = 50000.0
    engineering_cost_percent: float = 10.0
    contingency_percent: float = 15.0

@dataclass
class BESSSizingResult:
    """Class to hold BESS sizing calculation results"""
    # Battery calculations
    initial_battery_capacity_mwh: float
    after_dod_mwh: float
    after_static_eff_mwh: float
    after_cycle_eff_mwh: float
    after_derating_mwh: float
    required_discharging_power_mw: float
    battery_size_based_on_c_rate_mw: float
    is_battery_size_sufficient: bool
    required_battery_capacity_mwh: float
    
    # Battery selection
    proposed_battery_model: str
    proposed_battery_quantity: int
    battery_capacity_per_unit_kwh: float
    total_battery_capacity_mwh: float
    battery_chemistry: str
    battery_cycle_life: int
    battery_warranty_years: int
    
    # Charging parameters
    power_available_for_charging_mw: float
    time_to_fully_charge_hr: float
    
    # PCS selection
    proposed_pcs_model: str
    proposed_pcs_quantity: int
    pcs_power_per_unit_mw: float
    pcs_efficiency: float
    pcs_cooling_type: str
    
    # Transformer selection
    proposed_transformer_model: str
    proposed_transformer_quantity: int
    transformer_power_per_unit_mva: float
    transformer_type: str
    transformer_primary_kv: float
    transformer_secondary_kv: float
    transformer_step_type: str
    transformer_losses: float
    transformer_impedance: float
    transformer_mounting: str
    
    # Switchgear selection
    proposed_switchgear_model: str
    proposed_switchgear_quantity: int
    switchgear_voltage_kv: float
    switchgear_type: str
    switchgear_current_rating: float
    switchgear_breaking_capacity: float
    
    # AC Cabinet selection
    proposed_ac_cabinet_model: str
    proposed_ac_cabinet_quantity: int
    
    # EMS selection
    proposed_ems_model: str
    ems_features: str
    ems_hardware: str
    ems_software: str
    
    # Container selection
    proposed_container_model: str
    proposed_container_quantity: int
    container_dimensions: str
    
    # Cabling
    proposed_cabling_model: str
    cabling_length_m: float
    cabling_cost: float
    
    # Fire protection
    proposed_fire_system: str
    fire_system_cost: float
    
    # Costs
    total_equipment_cost: float
    site_prep_cost: float
    engineering_cost: float
    contingency_cost: float
    total_project_cost: float
    
    # Financial analysis
    lifecycle_years: float
    annual_degradation_percent: float
    transportation_logistics: Dict
    maintenance_costs: Dict
    financial_analysis: Dict

class BESSSizingCalculator:
    """Main class for BESS sizing calculations"""
    
    def __init__(self):
        self.input_params = None
        self.results = None
        
    def get_user_input(self):
        """Get input parameters from user"""
        print("=== BESS Sizing Calculator Input ===")
        print("Please enter the following parameters:")
        
        customer_load_mw = float(input("Customer Load (MW): "))
        discharge_duration_hr = float(input("Discharge Duration (Hours): "))
        c_rate = float(input("C-Rate (Max is 0.5C): "))
        grid_power_mw = float(input("Grid Power Available for Charging (MW): "))
        solar_power_mw = float(input("Solar Power Available for Charging (MW): "))
        other_power_mw = float(input("Other Power Available for Charging (MW): "))
        
        print("\nProject Application Options:")
        for i, app in enumerate(ProjectApplication, 1):
            print(f"{i}. {app.value}")
        app_idx = int(input("Select Project Application (1-7): ")) - 1
        project_application = list(ProjectApplication)[app_idx]
        
        print("\nAmbient Environment Options:")
        for i, env in enumerate(AmbientEnvironment, 1):
            print(f"{i}. {env.value}")
        env_idx = int(input("Select Ambient Environment (1-5): ")) - 1
        ambient_environment = list(AmbientEnvironment)[env_idx]
        
        voltage_standard_kv = float(input("Voltage Standard (kV): "))
        
        print("\nGrid Stability Options:")
        for i, stability in enumerate(GridStability, 1):
            print(f"{i}. {stability.value}")
        stability_idx = int(input("Select Grid Stability (1-4): ")) - 1
        grid_stability = list(GridStability)[stability_idx]
        
        print("\nCooling System Options:")
        for i, cooling in enumerate(CoolingSystem, 1):
            print(f"{i}. {cooling.value}")
        cooling_idx = int(input("Select Cooling System (1-4): ")) - 1
        cooling_system = list(CoolingSystem)[cooling_idx]
        
        cycles_per_day = int(input("Charge/Discharge Cycles per Day: "))
        black_start_required = input("Black Start Capability Required? (y/n): ").lower() == 'y'
        
        # Optional advanced parameters
        print("\nAdvanced Parameters (press Enter for default values):")
        dod_percent = float(input(f"Depth of Discharge (%) [Default: 90]: ") or 90.0)
        static_efficiency_percent = float(input(f"Static Efficiency (%) [Default: 90]: ") or 90.0)
        cycle_efficiency_percent = float(input(f"Cycle Efficiency (%) [Default: 95]: ") or 95.0)
        power_factor = float(input(f"Power Factor [Default: 0.95]: ") or 0.95)
        aging_derate_percent = float(input(f"Aging Derate (%) [Default: 5]: ") or 5.0)
        temperature_derate_percent = float(input(f"Temperature Derate (%) [Default: 3]: ") or 3.0)
        auxiliary_load_percent = float(input(f"Auxiliary Load (%) [Default: 2]: ") or 2.0)
        cable_length_m = float(input(f"Cable Length (m) [Default: 50]: ") or 50.0)
        site_prep_cost = float(input(f"Site Preparation Cost ($) [Default: 50000]: ") or 50000.0)
        
        charging_c_rate_input = input("Charging C-Rate (press Enter to use same as discharging): ")
        charging_c_rate = float(charging_c_rate_input) if charging_c_rate_input else c_rate
        
        self.input_params = BESSSizingInput(
            customer_load_mw=customer_load_mw,
            discharge_duration_hr=discharge_duration_hr,
            c_rate=c_rate,
            grid_power_mw=grid_power_mw,
            solar_power_mw=solar_power_mw,
            other_power_mw=other_power_mw,
            project_application=project_application,
            ambient_environment=ambient_environment,
            voltage_standard_kv=voltage_standard_kv,
            grid_stability=grid_stability,
            cooling_system=cooling_system,
            cycles_per_day=cycles_per_day,
            black_start_required=black_start_required,
            dod_percent=dod_percent,
            static_efficiency_percent=static_efficiency_percent,
            cycle_efficiency_percent=cycle_efficiency_percent,
            power_factor=power_factor,
            aging_derate_percent=aging_derate_percent,
            temperature_derate_percent=temperature_derate_percent,
            auxiliary_load_percent=auxiliary_load_percent,
            charging_c_rate=charging_c_rate,
            cable_length_m=cable_length_m,
            site_prep_cost=site_prep_cost
        )
        
        return self.input_params
    
    def calculate(self, input_params: BESSSizingInput) -> BESSSizingResult:
        """Perform all BESS sizing calculations"""
        self.input_params = input_params
        p = self.input_params
        
        # 1. Battery capacity calculations
        initial_battery_capacity_mwh = p.customer_load_mw * p.discharge_duration_hr
        after_dod_mwh = initial_battery_capacity_mwh / (p.dod_percent / 100)
        after_static_eff_mwh = after_dod_mwh / (p.static_efficiency_percent / 100)
        after_cycle_eff_mwh = after_static_eff_mwh / (p.cycle_efficiency_percent / 100)
        
        # Apply derating factors
        derating_factor = (1 - p.aging_derate_percent/100) * (1 - p.temperature_derate_percent/100) * (1 - p.auxiliary_load_percent/100)
        after_derating_mwh = after_cycle_eff_mwh / derating_factor
        
        # 2. Discharging parameters
        required_discharging_power_mw = p.customer_load_mw
        battery_size_based_on_c_rate_mw = required_discharging_power_mw / p.c_rate
        is_battery_size_sufficient = after_derating_mwh >= battery_size_based_on_c_rate_mw
        
        # Determine required battery capacity
        if is_battery_size_sufficient:
            required_battery_capacity_mwh = after_derating_mwh
        else:
            required_battery_capacity_mwh = battery_size_based_on_c_rate_mw
        
        # 3. Select battery model
        proposed_battery_model, proposed_battery_quantity, total_battery_capacity_mwh = self.select_battery_model(required_battery_capacity_mwh)
        battery_specs = BATTERY_MODELS[proposed_battery_model]
        
        # 4. Charging parameters
        power_available_for_charging_mw = p.grid_power_mw + p.solar_power_mw + p.other_power_mw
        min_charging_power = min(power_available_for_charging_mw, p.charging_c_rate * required_battery_capacity_mwh)
        time_to_fully_charge_hr = math.ceil((required_battery_capacity_mwh / (p.static_efficiency_percent/100) / (p.cycle_efficiency_percent/100)) / min_charging_power * 10) / 10
        
        # 5. Select PCS model
        max_discharge_power = required_battery_capacity_mwh * p.c_rate
        proposed_pcs_model, proposed_pcs_quantity = self.select_pcs_model(max_discharge_power)
        pcs_specs = PCS_MODELS[proposed_pcs_model]
        
        # 6. Select transformer
        transformer_power_mva = max_discharge_power / p.power_factor
        proposed_transformer_model, proposed_transformer_quantity, transformer_type = self.select_transformer_model(transformer_power_mva, p.voltage_standard_kv)
        transformer_specs = TRANSFORMER_MODELS[proposed_transformer_model]
        
        # Determine transformer parameters
        transformer_primary_kv = 0.69  # Standard PCS output voltage
        transformer_secondary_kv = p.voltage_standard_kv
        transformer_step_type = "Step-Up Transformer" if transformer_primary_kv < transformer_secondary_kv else "Step-Down Transformer"
        
        # 7. Select switchgear
        proposed_switchgear_model, proposed_switchgear_quantity = self.select_switchgear(p.voltage_standard_kv, max_discharge_power)
        switchgear_specs = SWITCHGEAR_MODELS[proposed_switchgear_model]
        
        # 8. Select AC cabinet
        proposed_ac_cabinet_model, proposed_ac_cabinet_quantity = self.select_ac_cabinet(proposed_pcs_quantity)
        
        # 9. Select EMS/SCADA
        proposed_ems_model = self.select_ems_system(p.project_application)
        ems_specs = EMS_SCADA_SYSTEMS[proposed_ems_model]
        
        # 10. Select containerization
        proposed_container_model, proposed_container_quantity = self.select_containerization(total_battery_capacity_mwh)
        container_specs = CONTAINER_OPTIONS[proposed_container_model]
        
        # 11. Select cabling
        proposed_cabling_model, cabling_cost = self.select_cabling(p.voltage_standard_kv, max_discharge_power, p.cable_length_m)
        
        # 12. Select fire protection
        proposed_fire_system, fire_system_cost = self.select_fire_protection(total_battery_capacity_mwh)
        
        # 13. Calculate costs
        total_equipment_cost = self.calculate_equipment_cost(
            proposed_battery_model, proposed_battery_quantity,
            proposed_pcs_model, proposed_pcs_quantity,
            proposed_transformer_model, proposed_transformer_quantity,
            proposed_switchgear_model, proposed_switchgear_quantity,
            proposed_ac_cabinet_model, proposed_ac_cabinet_quantity,
            proposed_ems_model,
            proposed_container_model, proposed_container_quantity,
            cabling_cost,
            fire_system_cost
        )
        
        engineering_cost = total_equipment_cost * (p.engineering_cost_percent / 100)
        contingency_cost = (total_equipment_cost + engineering_cost + p.site_prep_cost) * (p.contingency_percent / 100)
        total_project_cost = total_equipment_cost + engineering_cost + p.site_prep_cost + contingency_cost
        
        # 14. Lifecycle calculations
        lifecycle_years = self.calculate_lifecycle_years(p.cycles_per_day, battery_specs["cycle_life"])
        annual_degradation_percent = self.calculate_annual_degradation()
        
        # 15. Transportation logistics
        transportation_logistics = self.calculate_transportation_logistics(
            proposed_battery_model, proposed_battery_quantity,
            proposed_container_model, proposed_container_quantity,
            proposed_transformer_model, proposed_transformer_quantity,
            proposed_pcs_model, proposed_pcs_quantity
        )
        
        # 16. Maintenance costs
        maintenance_costs = self.calculate_maintenance_costs(total_project_cost, battery_specs["cycle_life"], lifecycle_years)
        
        # 17. Financial analysis
        financial_analysis = self.calculate_financial_analysis(
            total_project_cost, required_battery_capacity_mwh, 
            p.customer_load_mw, p.discharge_duration_hr, p.cycles_per_day,
            p.project_application
        )
        
        # Create and return results object
        self.results = BESSSizingResult(
            # Battery calculations
            initial_battery_capacity_mwh=round(initial_battery_capacity_mwh, 2),
            after_dod_mwh=round(after_dod_mwh, 2),
            after_static_eff_mwh=round(after_static_eff_mwh, 2),
            after_cycle_eff_mwh=round(after_cycle_eff_mwh, 2),
            after_derating_mwh=round(after_derating_mwh, 2),
            required_discharging_power_mw=round(required_discharging_power_mw, 2),
            battery_size_based_on_c_rate_mw=round(battery_size_based_on_c_rate_mw, 2),
            is_battery_size_sufficient=is_battery_size_sufficient,
            required_battery_capacity_mwh=round(required_battery_capacity_mwh, 2),
            
            # Battery selection
            proposed_battery_model=proposed_battery_model,
            proposed_battery_quantity=proposed_battery_quantity,
            battery_capacity_per_unit_kwh=battery_specs["capacity_kwh"],
            total_battery_capacity_mwh=round(total_battery_capacity_mwh, 2),
            battery_chemistry=battery_specs["chemistry"],
            battery_cycle_life=battery_specs["cycle_life"],
            battery_warranty_years=battery_specs["warranty_years"],
            
            # Charging parameters
            power_available_for_charging_mw=round(power_available_for_charging_mw, 2),
            time_to_fully_charge_hr=round(time_to_fully_charge_hr, 1),
            
            # PCS selection
            proposed_pcs_model=proposed_pcs_model,
            proposed_pcs_quantity=proposed_pcs_quantity,
            pcs_power_per_unit_mw=pcs_specs["power_mw"],
            pcs_efficiency=pcs_specs["efficiency"],
            pcs_cooling_type=pcs_specs["cooling"],
            
            # Transformer selection
            proposed_transformer_model=proposed_transformer_model,
            proposed_transformer_quantity=proposed_transformer_quantity,
            transformer_power_per_unit_mva=transformer_specs["power_mva"],
            transformer_type=transformer_specs["type"].value,
            transformer_primary_kv=transformer_primary_kv,
            transformer_secondary_kv=transformer_secondary_kv,
            transformer_step_type=transformer_step_type,
            transformer_losses=transformer_specs["losses"],
            transformer_impedance=transformer_specs["impedance"],
            transformer_mounting=transformer_specs["mounting"].value,
            
            # Switchgear selection
            proposed_switchgear_model=proposed_switchgear_model,
            proposed_switchgear_quantity=proposed_switchgear_quantity,
            switchgear_voltage_kv=switchgear_specs["voltage_kv"],
            switchgear_type=switchgear_specs["type"],
            switchgear_current_rating=switchgear_specs["current_rating"],
            switchgear_breaking_capacity=switchgear_specs["breaking_capacity"],
            
            # AC Cabinet selection
            proposed_ac_cabinet_model=proposed_ac_cabinet_model,
            proposed_ac_cabinet_quantity=proposed_ac_cabinet_quantity,
            
            # EMS selection
            proposed_ems_model=proposed_ems_model,
            ems_features=ems_specs["features"],
            ems_hardware=ems_specs["hardware"],
            ems_software=ems_specs["software"],
            
            # Container selection
            proposed_container_model=proposed_container_model,
            proposed_container_quantity=proposed_container_quantity,
            container_dimensions=container_specs["dimensions"],
            
            # Cabling
            proposed_cabling_model=proposed_cabling_model,
            cabling_length_m=p.cable_length_m,
            cabling_cost=round(cabling_cost, 2),
            
            # Fire protection
            proposed_fire_system=proposed_fire_system,
            fire_system_cost=round(fire_system_cost, 2),
            
            # Costs
            total_equipment_cost=round(total_equipment_cost, 2),
            site_prep_cost=round(p.site_prep_cost, 2),
            engineering_cost=round(engineering_cost, 2),
            contingency_cost=round(contingency_cost, 2),
            total_project_cost=round(total_project_cost, 2),
            
            # Financial analysis
            lifecycle_years=round(lifecycle_years, 1),
            annual_degradation_percent=round(annual_degradation_percent, 2),
            transportation_logistics=transportation_logistics,
            maintenance_costs=maintenance_costs,
            financial_analysis=financial_analysis
        )
        
        return self.results
    
    def select_battery_model(self, required_capacity_mwh: float) -> Tuple[str, int, float]:
        """Select the most appropriate battery model based on required capacity"""
        # Convert to kWh for comparison
        required_capacity_kwh = required_capacity_mwh * 1000
        
        # Find the best battery model
        best_model = None
        best_quantity = 0
        best_total_capacity = 0
        min_waste = float('inf')
        
        for model, specs in BATTERY_MODELS.items():
            capacity_per_unit = specs["capacity_kwh"]
            quantity = math.ceil(required_capacity_kwh / capacity_per_unit)
            total_capacity = quantity * capacity_per_unit
            waste = total_capacity - required_capacity_kwh
            
            if waste < min_waste or (waste == min_waste and quantity < best_quantity):
                best_model = model
                best_quantity = quantity
                best_total_capacity = total_capacity / 1000  # Convert back to MWh
                min_waste = waste
        
        return best_model, best_quantity, best_total_capacity
    
    def select_pcs_model(self, max_discharge_power_mw: float) -> Tuple[str, int]:
        """Select the most appropriate PCS model based on required power"""
        pcs_power_per_unit = 0
        best_model = None
        best_quantity = 0
        
        # Calculate required PCS quantity for each model
        for model, specs in PCS_MODELS.items():
            pcs_power = specs["power_mw"]
            quantity = math.ceil(max_discharge_power_mw / pcs_power)
            
            # Prefer models with less units and closer match to required power
            if best_model is None or quantity < best_quantity or (quantity == best_quantity and pcs_power > pcs_power_per_unit):
                best_model = model
                best_quantity = quantity
                pcs_power_per_unit = pcs_power
        
        return best_model, best_quantity
    
    def select_transformer_model(self, required_power_mva: float, voltage_kv: float) -> Tuple[str, int, TransformerType]:
        """Select the most appropriate transformer model"""
        best_model = None
        best_quantity = 0
        transformer_type = TransformerType.DRY
        
        for model, specs in TRANSFORMER_MODELS.items():
            transformer_power = specs["power_mva"]
            quantity = math.ceil(required_power_mva / transformer_power)
            
            # For higher voltages or powers, prefer oil-filled transformers
            if voltage_kv > 33 or required_power_mva > 10:
                if specs["type"] == TransformerType.OIL:
                    if best_model is None or quantity < best_quantity:
                        best_model = model
                        best_quantity = quantity
                        transformer_type = specs["type"]
            else:
                if best_model is None or quantity < best_quantity:
                    best_model = model
                    best_quantity = quantity
                    transformer_type = specs["type"]
        
        return best_model, best_quantity, transformer_type
    
    def select_switchgear(self, voltage_kv: float, max_power_mw: float) -> Tuple[str, int]:
        """Select appropriate switchgear based on voltage and power"""
        max_current = max_power_mw * 1000 / (voltage_kv * 1.732)  # 3-phase current calculation
        
        best_model = None
        best_quantity = 0
        
        for model, specs in SWITCHGEAR_MODELS.items():
            if abs(specs["voltage_kv"] - voltage_kv) <= 0.1:  # Match voltage level
                if specs["current_rating"] >= max_current:
                    best_model = model
                    best_quantity = 1
                    break
                else:
                    # If single unit can't handle current, need multiple in parallel
                    quantity = math.ceil(max_current / specs["current_rating"])
                    if best_model is None or quantity < best_quantity:
                        best_model = model
                        best_quantity = quantity
        
        return best_model, best_quantity
    
    def select_ac_cabinet(self, pcs_quantity: int) -> Tuple[str, int]:
        """Select AC cabinet based on PCS quantity"""
        best_model = None
        best_quantity = 0
        min_waste = float('inf')
        
        for model, specs in AC_CABINET_MODELS.items():
            capacity = specs["capacity_units"]
            quantity = math.ceil(pcs_quantity / capacity)
            waste = quantity * capacity - pcs_quantity
            
            if waste < min_waste:
                best_model = model
                best_quantity = quantity
                min_waste = waste
        
        return best_model, best_quantity
    
    def select_ems_system(self, project_application: ProjectApplication) -> str:
        """Select appropriate EMS/SCADA system based on project application"""
        if project_application in [ProjectApplication.FREQUENCY_REGULATION, ProjectApplication.MICROGRID, ProjectApplication.BLACK_START]:
            return "EMS-PRO"
        elif project_application in [ProjectApplication.PEAK_SHAVING, ProjectApplication.RENEWABLE_INTEGRATION]:
            return "EMS-ADV"
        else:
            return "EMS-BASIC"
    
    def select_containerization(self, total_battery_capacity_mwh: float) -> Tuple[str, int]:
        """Select appropriate containerization based on battery capacity"""
        total_battery_capacity_kwh = total_battery_capacity_mwh * 1000
        best_model = None
        best_quantity = 0
        min_waste = float('inf')
        
        for model, specs in CONTAINER_OPTIONS.items():
            if model == "CONT-CUSTOM":
                continue  # Consider custom only if standard options don't fit
                
            capacity = specs["capacity_kwh"]
            quantity = math.ceil(total_battery_capacity_kwh / capacity)
            waste = quantity * capacity - total_battery_capacity_kwh
            
            if waste < min_waste:
                best_model = model
                best_quantity = quantity
                min_waste = waste
        
        # If standard containers result in too much waste, consider custom
        if min_waste > total_battery_capacity_kwh * 0.3:  # If waste > 30% of capacity
            best_model = "CONT-CUSTOM"
            best_quantity = math.ceil(total_battery_capacity_kwh / CONTAINER_OPTIONS["CONT-CUSTOM"]["capacity_kwh"])
        
        return best_model, best_quantity
    
    def select_cabling(self, voltage_kv: float, max_power_mw: float, cable_length_m: float) -> Tuple[str, float]:
        """Select appropriate cabling based on voltage and power"""
        max_current = max_power_mw * 1000 / (voltage_kv * 1.732)  # 3-phase current calculation
        
        if voltage_kv <= 1:
            cabling_model = "CAB-LV"
        elif voltage_kv <= 36:
            cabling_model = "CAB-MV"
        else:
            cabling_model = "CAB-HV"
        
        cabling_cost = CABLING_OPTIONS[cabling_model]["cost_per_m"] * cable_length_m
        
        return cabling_model, cabling_cost
    
    def select_fire_protection(self, total_battery_capacity_mwh: float) -> Tuple[str, float]:
        """Select appropriate fire protection system based on battery capacity"""
        if total_battery_capacity_mwh <= 5:
            return "FIRE-AFSS", FIRE_PROTECTION_SYSTEMS["FIRE-AFSS"]["cost"]
        elif total_battery_capacity_mwh <= 10:
            return "FIRE-WATER", FIRE_PROTECTION_SYSTEMS["FIRE-WATER"]["cost"]
        else:
            return "FIRE-FM200", FIRE_PROTECTION_SYSTEMS["FIRE-FM200"]["cost"]
    
    def calculate_equipment_cost(self, battery_model, battery_qty, 
                               pcs_model, pcs_qty,
                               transformer_model, transformer_qty,
                               switchgear_model, switchgear_qty,
                               ac_cabinet_model, ac_cabinet_qty,
                               ems_model,
                               container_model, container_qty,
                               cabling_cost,
                               fire_system_cost) -> float:
        """Calculate total equipment cost"""
        total_cost = 0
        
        # Battery cost
        battery_cost = BATTERY_MODELS[battery_model]["cost_per_kwh"] * BATTERY_MODELS[battery_model]["capacity_kwh"] * battery_qty
        total_cost += battery_cost
        
        # PCS cost
        total_cost += PCS_MODELS[pcs_model]["cost"] * pcs_qty
        
        # Transformer cost
        total_cost += TRANSFORMER_MODELS[transformer_model]["cost"] * transformer_qty
        
        # Switchgear cost
        total_cost += SWITCHGEAR_MODELS[switchgear_model]["cost"] * switchgear_qty
        
        # AC Cabinet cost
        total_cost += AC_CABINET_MODELS[ac_cabinet_model]["cost"] * ac_cabinet_qty
        
        # EMS cost
        total_cost += EMS_SCADA_SYSTEMS[ems_model]["cost"]
        
        # Container cost
        total_cost += CONTAINER_OPTIONS[container_model]["cost"] * container_qty
        
        # Cabling cost
        total_cost += cabling_cost
        
        # Fire protection cost
        total_cost += fire_system_cost
        
        return total_cost
    
    def calculate_lifecycle_years(self, cycles_per_day: int, battery_cycle_life: int) -> float:
        """Calculate expected lifecycle in years"""
        # Assuming 300 operating days per year
        annual_cycles = cycles_per_day * 300
        return battery_cycle_life / annual_cycles if annual_cycles > 0 else 0
    
    def calculate_annual_degradation(self) -> float:
        """Calculate annual degradation percentage"""
        # Typical lithium-ion battery degradation is 2-3% per year
        return 2.5
    
    def calculate_transportation_logistics(self, battery_model, battery_qty, 
                                         container_model, container_qty,
                                         transformer_model, transformer_qty,
                                         pcs_model, pcs_qty) -> Dict:
        """Calculate transportation logistics"""
        battery_weight = BATTERY_MODELS[battery_model]["weight_kg"] * battery_qty
        container_weight = CONTAINER_OPTIONS[container_model]["weight_kg"] * container_qty
        transformer_weight = TRANSFORMER_MODELS[transformer_model]["weight_kg"] * transformer_qty
        pcs_weight = PCS_MODELS[pcs_model]["weight_kg"] * pcs_qty
        
        total_weight_kg = battery_weight + container_weight + transformer_weight + pcs_weight
        total_weight_ton = total_weight_kg / 1000
        
        # Estimate number of trucks needed (assuming 20-ton capacity)
        trucks_needed = math.ceil(total_weight_ton / 20)
        
        return {
            "battery_weight_kg": round(battery_weight, 2),
            "container_weight_kg": round(container_weight, 2),
            "transformer_weight_kg": round(transformer_weight, 2),
            "pcs_weight_kg": round(pcs_weight, 2),
            "total_weight_kg": round(total_weight_kg, 2),
            "total_weight_ton": round(total_weight_ton, 2),
            "trucks_needed": trucks_needed
        }
    
    def calculate_maintenance_costs(self, total_project_cost: float, battery_cycle_life: int, lifecycle_years: float) -> Dict:
        """Calculate annual maintenance costs"""
        # Annual maintenance is typically 1-2% of project cost
        annual_maintenance = total_project_cost * 0.015
        
        # Battery replacement when cycle life is reached or after 10 years, whichever comes first
        battery_replacement_year = min(10, lifecycle_years)
        
        # Battery replacement cost (50% of battery cost, assuming battery cost is 60% of total project cost)
        battery_replacement_cost = total_project_cost * 0.6 * 0.5
        
        # Major maintenance at half lifecycle
        major_maintenance_year = lifecycle_years / 2
        major_maintenance_cost = total_project_cost * 0.1
        
        return {
            "annual_maintenance": round(annual_maintenance, 2),
            "battery_replacement_year": round(battery_replacement_year, 1),
            "battery_replacement_cost": round(battery_replacement_cost, 2),
            "major_maintenance_year": round(major_maintenance_year, 1),
            "major_maintenance_cost": round(major_maintenance_cost, 2)
        }
    
    def calculate_financial_analysis(self, total_project_cost: float, 
                                   battery_capacity_mwh: float,
                                   customer_load_mw: float,
                                   discharge_duration_hr: float,
                                   cycles_per_day: int,
                                   project_application: ProjectApplication) -> Dict:
        """Perform financial analysis"""
        # Determine value streams based on project application
        if project_application == ProjectApplication.PEAK_SHAVING:
            energy_value = 0.15  # $/kWh for peak shaving
            capacity_value = 100  # $/kW-year for capacity
        elif project_application == ProjectApplication.FREQUENCY_REGULATION:
            energy_value = 0.10  # $/kWh for frequency regulation
            capacity_value = 150  # $/kW-year for ancillary services
        elif project_application == ProjectApplication.SELF_CONSUMPTION:
            energy_value = 0.12  # $/kWh for self consumption
            capacity_value = 80   # $/kW-year for capacity
        else:
            energy_value = 0.10  # Default $/kWh
            capacity_value = 100  # Default $/kW-year
        
        # Calculate energy revenue
        daily_energy_kwh = customer_load_mw * 1000 * discharge_duration_hr * cycles_per_day
        daily_energy_revenue = daily_energy_kwh * energy_value
        annual_energy_revenue = daily_energy_revenue * 300  # 300 operating days
        
        # Calculate capacity revenue
        capacity_revenue = customer_load_mw * 1000 * capacity_value  # $/year
        
        # Total annual revenue
        annual_revenue = annual_energy_revenue + capacity_revenue
        
        # Simple payback period
        payback_years = total_project_cost / annual_revenue if annual_revenue > 0 else float('inf')
        
        # Levelized cost of storage (LCOS)
        # LCOS = (Total Cost + Total O&M) / Total Energy Discharged over lifetime
        lifecycle_years = self.calculate_lifecycle_years(cycles_per_day, 6000)  # Using standard 6000 cycles
        total_energy_discharged_kwh = daily_energy_kwh * 300 * lifecycle_years
        total_om_cost = self.calculate_maintenance_costs(total_project_cost, 6000, lifecycle_years)["annual_maintenance"] * lifecycle_years
        lcos = (total_project_cost + total_om_cost) / total_energy_discharged_kwh if total_energy_discharged_kwh > 0 else 0
        
        # Net Present Value (NPV) calculation
        discount_rate = 0.08  # 8% discount rate
        npv = -total_project_cost
        for year in range(1, int(lifecycle_years) + 1):
            npv += annual_revenue / ((1 + discount_rate) ** year)
        
        # Internal Rate of Return (IRR) approximation
        if annual_revenue > 0:
            irr_approx = (annual_revenue / total_project_cost) * 100
        else:
            irr_approx = 0
        
        return {
            "total_project_cost": round(total_project_cost, 2),
            "daily_energy_kwh": round(daily_energy_kwh, 2),
            "daily_energy_revenue": round(daily_energy_revenue, 2),
            "annual_energy_revenue": round(annual_energy_revenue, 2),
            "capacity_revenue": round(capacity_revenue, 2),
            "annual_revenue": round(annual_revenue, 2),
            "payback_years": round(payback_years, 2),
            "lcos_per_kwh": round(lcos, 4),
            "npv": round(npv, 2),
            "irr_approx": round(irr_approx, 2)
        }
    
    def generate_recommendations(self) -> List[Dict]:
        """Generate multiple design options with cost-effectiveness analysis"""
        if not self.results:
            return []
        
        options = []
        
        # Option 1: Base design (as calculated)
        options.append({
            "name": "Base Design",
            "battery_model": self.results.proposed_battery_model,
            "battery_qty": self.results.proposed_battery_quantity,
            "pcs_model": self.results.proposed_pcs_model,
            "pcs_qty": self.results.proposed_pcs_quantity,
            "transformer_model": self.results.proposed_transformer_model,
            "transformer_qty": self.results.proposed_transformer_quantity,
            "switchgear_model": self.results.proposed_switchgear_model,
            "switchgear_qty": self.results.proposed_switchgear_quantity,
            "total_cost": self.results.total_project_cost,
            "payback_years": self.results.financial_analysis["payback_years"],
            "description": "Optimized design based on your requirements with best balance of cost and performance."
        })
        
        # Option 2: Higher battery capacity for longer autonomy
        battery_model_2, battery_qty_2, _ = self.select_battery_model(
            self.results.required_battery_capacity_mwh * 1.2
        )
        
        # Recalculate costs for option 2
        cost_2 = self.calculate_equipment_cost(
            battery_model_2, battery_qty_2,
            self.results.proposed_pcs_model, self.results.proposed_pcs_quantity,
            self.results.proposed_transformer_model, self.results.proposed_transformer_quantity,
            self.results.proposed_switchgear_model, self.results.proposed_switchgear_quantity,
            self.results.proposed_ac_cabinet_model, self.results.proposed_ac_cabinet_quantity,
            self.results.proposed_ems_model,
            self.results.proposed_container_model, self.results.proposed_container_quantity,
            self.results.cabling_cost,
            self.results.fire_system_cost
        )
        
        # Add engineering, site prep, and contingency
        cost_2 = cost_2 * (1 + self.input_params.engineering_cost_percent/100) + \
                self.input_params.site_prep_cost
        cost_2 = cost_2 * (1 + self.input_params.contingency_percent/100)
        
        options.append({
            "name": "Extended Autonomy Design",
            "battery_model": battery_model_2,
            "battery_qty": battery_qty_2,
            "pcs_model": self.results.proposed_pcs_model,
            "pcs_qty": self.results.proposed_pcs_quantity,
            "transformer_model": self.results.proposed_transformer_model,
            "transformer_qty": self.results.proposed_transformer_quantity,
            "switchgear_model": self.results.proposed_switchgear_model,
            "switchgear_qty": self.results.proposed_switchgear_quantity,
            "total_cost": cost_2,
            "payback_years": cost_2 / (self.results.financial_analysis["annual_revenue"] or 1),
            "description": "20% additional battery capacity for extended backup time and improved cycle life."
        })
        
        # Option 3: Lower cost design with smaller battery
        if self.results.required_battery_capacity_mwh > 1:
            battery_model_3, battery_qty_3, _ = self.select_battery_model(
                self.results.required_battery_capacity_mwh * 0.8
            )
            
            cost_3 = self.calculate_equipment_cost(
                battery_model_3, battery_qty_3,
                self.results.proposed_pcs_model, self.results.proposed_pcs_quantity,
                self.results.proposed_transformer_model, self.results.proposed_transformer_quantity,
                self.results.proposed_switchgear_model, self.results.proposed_switchgear_quantity,
                self.results.proposed_ac_cabinet_model, self.results.proposed_ac_cabinet_quantity,
                self.results.proposed_ems_model,
                self.results.proposed_container_model, self.results.proposed_container_quantity,
                self.results.cabling_cost,
                self.results.fire_system_cost
            )
            
            # Add engineering, site prep, and contingency
            cost_3 = cost_3 * (1 + self.input_params.engineering_cost_percent/100) + \
                    self.input_params.site_prep_cost
            cost_3 = cost_3 * (1 + self.input_params.contingency_percent/100)
            
            options.append({
                "name": "Cost-Optimized Design",
                "battery_model": battery_model_3,
                "battery_qty": battery_qty_3,
                "pcs_model": self.results.proposed_pcs_model,
                "pcs_qty": self.results.proposed_pcs_quantity,
                "transformer_model": self.results.proposed_transformer_model,
                "transformer_qty": self.results.proposed_transformer_quantity,
                "switchgear_model": self.results.proposed_switchgear_model,
                "switchgear_qty": self.results.proposed_switchgear_quantity,
                "total_cost": cost_3,
                "payback_years": cost_3 / (self.results.financial_analysis["annual_revenue"] or 1),
                "description": "20% reduced battery capacity for lower initial investment, suitable for applications with shorter backup requirements."
            })
        
        # Option 4: Higher efficiency design with better components
        # Use higher efficiency PCS and transformer if available
        pcs_model_4 = None
        for model, specs in PCS_MODELS.items():
            if specs["efficiency"] > 0.98 and specs["power_mw"] >= PCS_MODELS[self.results.proposed_pcs_model]["power_mw"] / self.results.proposed_pcs_quantity:
                pcs_model_4 = model
                break
        
        if not pcs_model_4:
            pcs_model_4 = self.results.proposed_pcs_model
        
        cost_4 = self.calculate_equipment_cost(
            self.results.proposed_battery_model, self.results.proposed_battery_quantity,
            pcs_model_4, self.results.proposed_pcs_quantity,
            self.results.proposed_transformer_model, self.results.proposed_transformer_quantity,
            self.results.proposed_switchgear_model, self.results.proposed_switchgear_quantity,
            self.results.proposed_ac_cabinet_model, self.results.proposed_ac_cabinet_quantity,
            "EMS-PRO",  # Upgrade EMS
            self.results.proposed_container_model, self.results.proposed_container_quantity,
            self.results.cabling_cost,
            self.results.fire_system_cost
        )
        
        # Add engineering, site prep, and contingency
        cost_4 = cost_4 * (1 + self.input_params.engineering_cost_percent/100) + \
                self.input_params.site_prep_cost
        cost_4 = cost_4 * (1 + self.input_params.contingency_percent/100)
        
        options.append({
            "name": "High-Efficiency Design",
            "battery_model": self.results.proposed_battery_model,
            "battery_qty": self.results.proposed_battery_quantity,
            "pcs_model": pcs_model_4,
            "pcs_qty": self.results.proposed_pcs_quantity,
            "transformer_model": self.results.proposed_transformer_model,
            "transformer_qty": self.results.proposed_transformer_quantity,
            "switchgear_model": self.results.proposed_switchgear_model,
            "switchgear_qty": self.results.proposed_switchgear_quantity,
            "total_cost": cost_4,
            "payback_years": cost_4 / (self.results.financial_analysis["annual_revenue"] or 1),
            "description": "Premium components with higher efficiency and advanced EMS for optimal performance and monitoring."
        })
        
        # Option 5: LFP battery chemistry for longer lifecycle
        # Find LFP battery with similar capacity
        lfp_battery_model = None
        for model, specs in BATTERY_MODELS.items():
            if specs["chemistry"] == "LFP" and abs(specs["capacity_kwh"] - self.results.battery_capacity_per_unit_kwh) / self.results.battery_capacity_per_unit_kwh <= 0.2:
                lfp_battery_model = model
                break
        
        if lfp_battery_model:
            battery_qty_5 = math.ceil(self.results.required_battery_capacity_mwh * 1000 / BATTERY_MODELS[lfp_battery_model]["capacity_kwh"])
            
            cost_5 = self.calculate_equipment_cost(
                lfp_battery_model, battery_qty_5,
                self.results.proposed_pcs_model, self.results.proposed_pcs_quantity,
                self.results.proposed_transformer_model, self.results.proposed_transformer_quantity,
                self.results.proposed_switchgear_model, self.results.proposed_switchgear_quantity,
                self.results.proposed_ac_cabinet_model, self.results.proposed_ac_cabinet_quantity,
                self.results.proposed_ems_model,
                self.results.proposed_container_model, self.results.proposed_container_quantity,
                self.results.cabling_cost,
                self.results.fire_system_cost
            )
            
            # Add engineering, site prep, and contingency
            cost_5 = cost_5 * (1 + self.input_params.engineering_cost_percent/100) + \
                    self.input_params.site_prep_cost
            cost_5 = cost_5 * (1 + self.input_params.contingency_percent/100)
            
            options.append({
                "name": "LFP Long-Life Design",
                "battery_model": lfp_battery_model,
                "battery_qty": battery_qty_5,
                "pcs_model": self.results.proposed_pcs_model,
                "pcs_qty": self.results.proposed_pcs_quantity,
                "transformer_model": self.results.proposed_transformer_model,
                "transformer_qty": self.results.proposed_transformer_quantity,
                "switchgear_model": self.results.proposed_switchgear_model,
                "switchgear_qty": self.results.proposed_switchgear_quantity,
                "total_cost": cost_5,
                "payback_years": cost_5 / (self.results.financial_analysis["annual_revenue"] or 1),
                "description": "LFP battery chemistry for enhanced safety and longer cycle life (6000+ cycles), ideal for daily cycling applications."
            })
        
        # Option 6: Modular design with smaller units for scalability
        if self.results.proposed_battery_quantity > 1:
            # Find a smaller battery model that would require more units but allow better scalability
            smaller_battery_model = None
            for model, specs in BATTERY_MODELS.items():
                if specs["capacity_kwh"] < self.results.battery_capacity_per_unit_kwh and specs["capacity_kwh"] >= 1000:
                    smaller_battery_model = model
                    break
            
            if smaller_battery_model:
                battery_qty_6 = math.ceil(self.results.required_battery_capacity_mwh * 1000 / BATTERY_MODELS[smaller_battery_model]["capacity_kwh"])
                
                # May need more PCS units if the smaller batteries are distributed
                pcs_qty_6 = max(self.results.proposed_pcs_quantity, math.ceil(battery_qty_6 / 4))  # Assume 4 batteries per PCS
                
                cost_6 = self.calculate_equipment_cost(
                    smaller_battery_model, battery_qty_6,
                    self.results.proposed_pcs_model, pcs_qty_6,
                    self.results.proposed_transformer_model, self.results.proposed_transformer_quantity,
                    self.results.proposed_switchgear_model, self.results.proposed_switchgear_quantity,
                    self.results.proposed_ac_cabinet_model, self.results.proposed_ac_cabinet_quantity,
                    self.results.proposed_ems_model,
                    self.results.proposed_container_model, self.results.proposed_container_quantity,
                    self.results.cabling_cost,
                    self.results.fire_system_cost
                )
                
                # Add engineering, site prep, and contingency
                cost_6 = cost_6 * (1 + self.input_params.engineering_cost_percent/100) + \
                        self.input_params.site_prep_cost
                cost_6 = cost_6 * (1 + self.input_params.contingency_percent/100)
                
                options.append({
                    "name": "Modular Scalable Design",
                    "battery_model": smaller_battery_model,
                    "battery_qty": battery_qty_6,
                    "pcs_model": self.results.proposed_pcs_model,
                    "pcs_qty": pcs_qty_6,
                    "transformer_model": self.results.proposed_transformer_model,
                    "transformer_qty": self.results.proposed_transformer_quantity,
                    "switchgear_model": self.results.proposed_switchgear_model,
                    "switchgear_qty": self.results.proposed_switchgear_quantity,
                    "total_cost": cost_6,
                    "payback_years": cost_6 / (self.results.financial_analysis["annual_revenue"] or 1),
                    "description": "Modular design with smaller units for easier expansion and redundancy, suitable for phased implementation."
                })
        
        # Sort options by total cost
        options.sort(key=lambda x: x["total_cost"])
        
        return options
    
    def generate_pdf_report(self, filename: str):
        """Generate a professional PDF report with detailed information"""
        if not self.results:
            raise ValueError("No calculation results available. Run calculate() first.")
        
        pdf = FPDF()
        pdf.add_page()
        
        # Title
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "BESS Sizing Calculator Report", 0, 1, "C")
        pdf.ln(10)
        
        # Input Parameters Section
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "1. Input Parameters", 0, 1)
        pdf.set_font("Arial", "", 12)
        
        input_data = [
            ["Customer Load", f"{self.input_params.customer_load_mw} MW"],
            ["Discharge Duration", f"{self.input_params.discharge_duration_hr} hours"],
            ["C-Rate", f"{self.input_params.c_rate}C"],
            ["Grid Power Available", f"{self.input_params.grid_power_mw} MW"],
            ["Solar Power Available", f"{self.input_params.solar_power_mw} MW"],
            ["Other Power Available", f"{self.input_params.other_power_mw} MW"],
            ["Project Application", self.input_params.project_application.value],
            ["Ambient Environment", self.input_params.ambient_environment.value],
            ["Voltage Standard", f"{self.input_params.voltage_standard_kv} kV"],
            ["Grid Stability", self.input_params.grid_stability.value],
            ["Cooling System", self.input_params.cooling_system.value],
            ["Cycles per Day", str(self.input_params.cycles_per_day)],
            ["Black Start Required", "Yes" if self.input_params.black_start_required else "No"],
            ["Depth of Discharge", f"{self.input_params.dod_percent}%"],
            ["Static Efficiency", f"{self.input_params.static_efficiency_percent}%"],
            ["Cycle Efficiency", f"{self.input_params.cycle_efficiency_percent}%"],
            ["Power Factor", str(self.input_params.power_factor)],
            ["Aging Derate", f"{self.input_params.aging_derate_percent}%"],
            ["Temperature Derate", f"{self.input_params.temperature_derate_percent}%"],
            ["Auxiliary Load", f"{self.input_params.auxiliary_load_percent}%"],
            ["Charging C-Rate", f"{self.input_params.charging_c_rate}C"],
            ["Cable Length", f"{self.input_params.cable_length_m} m"],
            ["Site Preparation Cost", f"${self.input_params.site_prep_cost:,.2f}"],
        ]
        
        for item in input_data:
            pdf.cell(90, 8, item[0] + ":", 0, 0)
            pdf.cell(0, 8, item[1], 0, 1)
        
        pdf.ln(10)
        
        # Calculation Results Section
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "2. Calculation Results", 0, 1)
        pdf.set_font("Arial", "", 12)
        
        # Battery Sizing
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, "Battery Sizing Calculations:", 0, 1)
        pdf.set_font("Arial", "", 12)
        
        battery_calc_data = [
            ["Initial Battery Capacity", f"{self.results.initial_battery_capacity_mwh} MWh", "Customer Load × Discharge Duration"],
            ["After DoD Adjustment", f"{self.results.after_dod_mwh} MWh", "Initial Capacity ÷ (DoD %)"],
            ["After Static Efficiency", f"{self.results.after_static_eff_mwh} MWh", "After DoD ÷ Static Efficiency"],
            ["After Cycle Efficiency", f"{self.results.after_cycle_eff_mwh} MWh", "After Static Eff ÷ Cycle Efficiency"],
            ["After Derating Factors", f"{self.results.after_derating_mwh} MWh", "After Cycle Eff ÷ Derating Factors"],
            ["Required Discharging Power", f"{self.results.required_discharging_power_mw} MW", "Customer Load"],
            ["Battery Size Based on C-Rate", f"{self.results.battery_size_based_on_c_rate_mw} MW", "Required Power ÷ C-Rate"],
            ["Battery Size Sufficient", "Yes" if self.results.is_battery_size_sufficient else "No", ""],
            ["Required Battery Capacity", f"{self.results.required_battery_capacity_mwh} MWh", "Final calculated capacity"],
        ]
        
        for item in battery_calc_data:
            pdf.cell(70, 8, item[0], 0, 0)
            pdf.cell(40, 8, item[1], 0, 0)
            pdf.cell(0, 8, item[2], 0, 1)
        
        pdf.ln(5)
        
        # Charging Calculations
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, "Charging Calculations:", 0, 1)
        pdf.set_font("Arial", "", 12)
        
        charging_data = [
            ["Power Available for Charging", f"{self.results.power_available_for_charging_mw} MW", "Grid + Solar + Other Power"],
            ["Time to Fully Charge", f"{self.results.time_to_fully_charge_hr} hours", "Battery Capacity ÷ Charging Power ÷ Efficiency"],
        ]
        
        for item in charging_data:
            pdf.cell(70, 8, item[0], 0, 0)
            pdf.cell(40, 8, item[1], 0, 0)
            pdf.cell(0, 8, item[2], 0, 1)
        
        pdf.ln(10)
        
        # Bill of Quantity Section
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "3. Bill of Quantity (BOQ)", 0, 1)
        pdf.set_font("Arial", "", 12)
        
        boq_data = [
            ["Battery System", self.results.proposed_battery_model, self.results.proposed_battery_quantity],
            ["Power Conversion System", self.results.proposed_pcs_model, self.results.proposed_pcs_quantity],
            ["Transformer", self.results.proposed_transformer_model, self.results.proposed_transformer_quantity],
            ["Switchgear/RMU", self.results.proposed_switchgear_model, self.results.proposed_switchgear_quantity],
            ["AC System Cabinet", self.results.proposed_ac_cabinet_model, self.results.proposed_ac_cabinet_quantity],
            ["EMS & SCADA System", self.results.proposed_ems_model, 1],
            ["Containerization", self.results.proposed_container_model, self.results.proposed_container_quantity],
            ["Cabling", self.results.proposed_cabling_model, f"{self.results.cabling_length_m}m"],
            ["Fire Protection", self.results.proposed_fire_system, 1],
        ]
        
        pdf.cell(70, 8, "Component", 1, 0, "C")
        pdf.cell(70, 8, "Model", 1, 0, "C")
        pdf.cell(50, 8, "Quantity", 1, 1, "C")
        
        for item in boq_data:
            pdf.cell(70, 8, item[0], 1, 0)
            pdf.cell(70, 8, item[1], 1, 0)
            pdf.cell(50, 8, str(item[2]), 1, 1, "C")
        
        pdf.ln(10)
        
        # Battery Details
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, "Battery System Details:", 0, 1)
        pdf.set_font("Arial", "", 12)
        
        battery_details = [
            ["Model", self.results.proposed_battery_model],
            ["Quantity", str(self.results.proposed_battery_quantity)],
            ["Capacity per Unit", f"{self.results.battery_capacity_per_unit_kwh} kWh"],
            ["Total Capacity", f"{self.results.total_battery_capacity_mwh} MWh"],
            ["Chemistry", self.results.battery_chemistry],
            ["Cycle Life", f"{self.results.battery_cycle_life} cycles"],
            ["Warranty", f"{self.results.battery_warranty_years} years"],
        ]
        
        for item in battery_details:
            pdf.cell(50, 8, item[0] + ":", 0, 0)
            pdf.cell(0, 8, item[1], 0, 1)
        
        pdf.ln(5)
        
        # PCS Details
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, "PCS Details:", 0, 1)
        pdf.set_font("Arial", "", 12)
        
        pcs_details = [
            ["Model", self.results.proposed_pcs_model],
            ["Quantity", str(self.results.proposed_pcs_quantity)],
            ["Power per Unit", f"{self.results.pcs_power_per_unit_mw} MW"],
            ["Efficiency", f"{self.results.pcs_efficiency * 100}%"],
            ["Cooling Type", self.results.pcs_cooling_type],
        ]
        
        for item in pcs_details:
            pdf.cell(50, 8, item[0] + ":", 0, 0)
            pdf.cell(0, 8, item[1], 0, 1)
        
        pdf.ln(5)
        
        # Transformer Details
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, "Transformer Details:", 0, 1)
        pdf.set_font("Arial", "", 12)
        
        transformer_details = [
            ["Model", self.results.proposed_transformer_model],
            ["Quantity", str(self.results.proposed_transformer_quantity)],
            ["Power per Unit", f"{self.results.transformer_power_per_unit_mva} MVA"],
            ["Type", self.results.transformer_type],
            ["Primary Voltage", f"{self.results.transformer_primary_kv} kV"],
            ["Secondary Voltage", f"{self.results.transformer_secondary_kv} kV"],
            ["Configuration", self.results.transformer_step_type],
            ["Losses", f"{self.results.transformer_losses}%"],
            ["Impedance", f"{self.results.transformer_impedance}%"],
            ["Mounting", self.results.transformer_mounting],
        ]
        
        for item in transformer_details:
            pdf.cell(50, 8, item[0] + ":", 0, 0)
            pdf.cell(0, 8, item[1], 0, 1)
        
        pdf.ln(5)
        
        # Switchgear Details
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, "Switchgear Details:", 0, 1)
        pdf.set_font("Arial", "", 12)
        
        switchgear_details = [
            ["Model", self.results.proposed_switchgear_model],
            ["Quantity", str(self.results.proposed_switchgear_quantity)],
            ["Voltage Rating", f"{self.results.switchgear_voltage_kv} kV"],
            ["Type", self.results.switchgear_type],
            ["Current Rating", f"{self.results.switchgear_current_rating} A"],
            ["Breaking Capacity", f"{self.results.switchgear_breaking_capacity} kA"],
        ]
        
        for item in switchgear_details:
            pdf.cell(50, 8, item[0] + ":", 0, 0)
            pdf.cell(0, 8, item[1], 0, 1)
        
        pdf.ln(5)
        
        # EMS Details
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, "EMS/SCADA Details:", 0, 1)
        pdf.set_font("Arial", "", 12)
        
        ems_details = [
            ["Model", self.results.proposed_ems_model],
            ["Features", self.results.ems_features],
            ["Hardware", self.results.ems_hardware],
            ["Software", self.results.ems_software],
        ]
        
        pdf.cell(50, 8, ems_details[0][0] + ":", 0, 0)
        pdf.cell(0, 8, ems_details[0][1], 0, 1)
        
        # For multi-line features, we need to handle them separately
        pdf.cell(50, 8, ems_details[1][0] + ":", 0, 0)
        pdf.multi_cell(0, 8, ems_details[1][1])
        
        pdf.cell(50, 8, ems_details[2][0] + ":", 0, 0)
        pdf.cell(0, 8, ems_details[2][1], 0, 1)
        
        pdf.cell(50, 8, ems_details[3][0] + ":", 0, 0)
        pdf.cell(0, 8, ems_details[3][1], 0, 1)
        
        pdf.ln(5)
        
        # Container Details
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, "Container Details:", 0, 1)
        pdf.set_font("Arial", "", 12)
        
        container_details = [
            ["Model", self.results.proposed_container_model],
            ["Quantity", str(self.results.proposed_container_quantity)],
            ["Dimensions", self.results.container_dimensions],
        ]
        
        for item in container_details:
            pdf.cell(50, 8, item[0] + ":", 0, 0)
            pdf.cell(0, 8, item[1], 0, 1)
        
        pdf.ln(10)
        
        # Cost Breakdown Section
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "4. Cost Breakdown", 0, 1)
        pdf.set_font("Arial", "", 12)
        
        cost_data = [
            ["Equipment Cost", f"${self.results.total_equipment_cost:,.2f}"],
            ["Site Preparation", f"${self.results.site_prep_cost:,.2f}"],
            ["Engineering & Design", f"${self.results.engineering_cost:,.2f}"],
            ["Contingency", f"${self.results.contingency_cost:,.2f}"],
            ["Total Project Cost", f"${self.results.total_project_cost:,.2f}"],
        ]
        
        for item in cost_data:
            pdf.cell(80, 8, item[0] + ":", 0, 0)
            pdf.cell(0, 8, item[1], 0, 1)
        
        pdf.ln(10)
        
        # Financial Analysis Section
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "5. Financial Analysis", 0, 1)
        pdf.set_font("Arial", "", 12)
        
        financial_data = [
            ["Total Project Cost", f"${self.results.financial_analysis['total_project_cost']:,.2f}"],
            ["Daily Energy", f"{self.results.financial_analysis['daily_energy_kwh']:,.2f} kWh"],
            ["Daily Energy Revenue", f"${self.results.financial_analysis['daily_energy_revenue']:,.2f}"],
            ["Annual Energy Revenue", f"${self.results.financial_analysis['annual_energy_revenue']:,.2f}"],
            ["Capacity Revenue", f"${self.results.financial_analysis['capacity_revenue']:,.2f}"],
            ["Annual Revenue", f"${self.results.financial_analysis['annual_revenue']:,.2f}"],
            ["Payback Period", f"{self.results.financial_analysis['payback_years']:,.1f} years"],
            ["Levelized Cost of Storage", f"${self.results.financial_analysis['lcos_per_kwh']:,.4f}/kWh"],
            ["Net Present Value (NPV)", f"${self.results.financial_analysis['npv']:,.2f}"],
            ["Approximate IRR", f"{self.results.financial_analysis['irr_approx']:,.2f}%"],
            ["System Lifecycle", f"{self.results.lifecycle_years:,.1f} years"],
            ["Annual Degradation", f"{self.results.annual_degradation_percent}%"],
        ]
        
        for item in financial_data:
            pdf.cell(80, 8, item[0] + ":", 0, 0)
            pdf.cell(0, 8, item[1], 0, 1)
        
        pdf.ln(10)
        
        # Maintenance Costs
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, "Maintenance Costs:", 0, 1)
        pdf.set_font("Arial", "", 12)
        
        maintenance_data = [
            ["Annual Maintenance", f"${self.results.maintenance_costs['annual_maintenance']:,.2f}"],
            ["Battery Replacement (Year)", f"Year {self.results.maintenance_costs['battery_replacement_year']:,.1f}"],
            ["Battery Replacement Cost", f"${self.results.maintenance_costs['battery_replacement_cost']:,.2f}"],
            ["Major Maintenance (Year)", f"Year {self.results.maintenance_costs['major_maintenance_year']:,.1f}"],
            ["Major Maintenance Cost", f"${self.results.maintenance_costs['major_maintenance_cost']:,.2f}"],
        ]
        
        for item in maintenance_data:
            pdf.cell(80, 8, item[0] + ":", 0, 0)
            pdf.cell(0, 8, item[1], 0, 1)
        
        pdf.ln(10)
        
        # Transportation Logistics
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, "Transportation Logistics:", 0, 1)
        pdf.set_font("Arial", "", 12)
        
        transport_data = [
            ["Battery Weight", f"{self.results.transportation_logistics['battery_weight_kg']:,.2f} kg"],
            ["Container Weight", f"{self.results.transportation_logistics['container_weight_kg']:,.2f} kg"],
            ["Transformer Weight", f"{self.results.transportation_logistics['transformer_weight_kg']:,.2f} kg"],
            ["PCS Weight", f"{self.results.transportation_logistics['pcs_weight_kg']:,.2f} kg"],
            ["Total Weight", f"{self.results.transportation_logistics['total_weight_kg']:,.2f} kg ({self.results.transportation_logistics['total_weight_ton']:,.2f} tons)"],
            ["Trucks Required", f"{self.results.transportation_logistics['trucks_needed']}"],
        ]
        
        for item in transport_data:
            pdf.cell(80, 8, item[0] + ":", 0, 0)
            pdf.cell(0, 8, item[1], 0, 1)
        
        pdf.ln(10)
        
        # Design Recommendations
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "6. Design Recommendations", 0, 1)
        pdf.set_font("Arial", "", 9)
        
        recommendations = self.generate_recommendations()
        
        # Create a table for the recommendations
        pdf.cell(40, 8, "Design Option", 1, 0, "C")
        pdf.cell(30, 8, "Battery Qty", 1, 0, "C")
        pdf.cell(30, 8, "PCS Qty", 1, 0, "C")
        pdf.cell(40, 8, "Total Cost", 1, 0, "C")
        pdf.cell(50, 8, "Payback (Years)", 1, 1, "C")
        
        for option in recommendations:
            pdf.cell(40, 8, option["name"], 1, 0)
            pdf.cell(30, 8, str(option["battery_qty"]), 1, 0, "C")
            pdf.cell(30, 8, str(option["pcs_qty"]), 1, 0, "C")
            pdf.cell(40, 8, f"${option['total_cost']:,.2f}", 1, 0, "C")
            pdf.cell(50, 8, f"{option['payback_years']:.1f}", 1, 1, "C")
        
        pdf.ln(10)
        
        # Add descriptions for each recommendation
        for i, option in enumerate(recommendations, 1):
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 8, f"Option {i}: {option['name']}", 0, 1)
            pdf.set_font("Arial", "", 12)
            pdf.multi_cell(0, 8, option["description"])
            pdf.ln(5)
        
        # Final Recommendation
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, "Recommended Design:", 0, 1)
        pdf.set_font("Arial", "", 12)
        
        if recommendations:
            # Find the option with the best payback period
            best_option = min(recommendations, key=lambda x: x["payback_years"])
            pdf.multi_cell(0, 8, f"For the best return on investment, we recommend the {best_option['name']} with a payback period of {best_option['payback_years']:.1f} years. This option provides the optimal balance between initial investment and long-term financial returns.")
        
        pdf.ln(10)
        
        # Additional Considerations
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "7. Additional Considerations", 0, 1)
        pdf.set_font("Arial", "", 12)
        
        considerations = [
            "Site preparation may require additional civil works depending on soil conditions and local regulations.",
            "Grid connection approval from the local utility may be required and could involve additional costs.",
            "Environmental permits may be necessary, especially for larger installations.",
            "Regular maintenance is essential for optimal system performance and longevity.",
            "Consider future expansion possibilities when designing the layout and electrical infrastructure.",
            "Training for operations and maintenance staff should be included in the project planning.",
        ]
        
        for i, consideration in enumerate(considerations, 1):
            pdf.cell(10, 8, f"{i}.", 0, 0)
            pdf.multi_cell(0, 8, consideration)
        
        # Footer
        pdf.set_y(-15)
        pdf.set_font("Arial", "I", 8)
        pdf.cell(0, 10, f"Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 0, 0, "C")
        
        # Save PDF
        pdf.output(filename)
        print(f"PDF report generated: {filename}")

# ==================== MAIN EXECUTION ====================

def main():
    """Main function to run the BESS Sizing Calculator"""
    print("BESS Sizing Calculator")
    print("======================")
    
    # Create calculator instance
    calculator = BESSSizingCalculator()
    
    # Get user input
    input_params = calculator.get_user_input()
    
    # Perform calculations
    print("\nPerforming calculations...")
    results = calculator.calculate(input_params)
    
    # Generate PDF report
    report_filename = "bess_sizing_report.pdf"
    calculator.generate_pdf_report(report_filename)
    
    # Show summary
    print("\n=== CALCULATION SUMMARY ===")
    print(f"Required Battery Capacity: {results.required_battery_capacity_mwh} MWh")
    print(f"Proposed Battery System: {results.proposed_battery_quantity} x {results.proposed_battery_model}")
    print(f"Proposed PCS: {results.proposed_pcs_quantity} x {results.proposed_pcs_model}")
    print(f"Proposed Transformer: {results.proposed_transformer_quantity} x {results.proposed_transformer_model}")
    print(f"Proposed Switchgear: {results.proposed_switchgear_quantity} x {results.proposed_switchgear_model}")
    print(f"Total Project Cost: ${results.total_project_cost:,.2f}")
    print(f"Payback Period: {results.financial_analysis['payback_years']:.1f} years")
    
    # Show design recommendations
    recommendations = calculator.generate_recommendations()
    print("\n=== DESIGN RECOMMENDATIONS ===")
    for i, option in enumerate(recommendations, 1):
        print(f"{i}. {option['name']}: ${option['total_cost']:,.2f} (Payback: {option['payback_years']:.1f} years)")
        print(f"   {option['description']}")
        print()
    
    print(f"\nDetailed report saved as: {report_filename}")

if __name__ == "__main__":
    main()
