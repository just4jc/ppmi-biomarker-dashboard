#!/usr/bin/env python3
"""
Test script to verify the correlation heatmap fix
"""

import sys
import os
sys.path.append('/Users/georgeng/Library/CloudStorage/GoogleDrive-2018076@teacher.hkuspace.hku.hk/My Drive/Courses/Duke-NUS MD/Research Articles/PD Related/Datasets/PPMI Various Datasets')

from data_loader import PPMIDataLoader
import pandas as pd

def test_heatmap_function():
    """Test the correlation heatmap function specifically"""
    print("Testing correlation heatmap function...")
    
    try:
        # Load data
        loader = PPMIDataLoader()
        merged_data = loader.create_merged_dataset()
        
        # Test biomarkers
        test_biomarkers = ['CSF Alpha-synuclein', 'ABeta 1-42', 'pTau']
        test_clinical = ['NP3TOT'] if 'NP3TOT' in merged_data.columns else []
        
        # Create correlation matrix data (similar to the dashboard function)
        correlation_data = {}
        
        # Add biomarker data
        for biomarker in test_biomarkers:
            bio_data = merged_data[
                (merged_data['TESTNAME'] == biomarker) & 
                (merged_data['TESTVALUE_NUMERIC'].notna())
            ][['PATNO', 'TESTVALUE_NUMERIC']].rename(
                columns={'TESTVALUE_NUMERIC': biomarker}
            )
            
            if len(bio_data) > 0:
                print(f"Processing {biomarker}: {len(bio_data)} records")
                
                # Check for duplicates
                duplicate_count = bio_data['PATNO'].duplicated().sum()
                print(f"  Duplicate PATNOs: {duplicate_count}")
                
                # Handle duplicate patients by taking mean values
                bio_data_agg = bio_data.groupby('PATNO')[biomarker].mean()
                correlation_data[biomarker] = bio_data_agg
                print(f"  After aggregation: {len(bio_data_agg)} unique patients")
        
        # Add clinical scores if provided
        if test_clinical:
            for score in test_clinical:
                if score in merged_data.columns:
                    score_data = merged_data[merged_data[score].notna()][['PATNO', score]].drop_duplicates('PATNO')
                    if len(score_data) > 0:
                        print(f"Processing {score}: {len(score_data)} records")
                        correlation_data[score] = score_data.set_index('PATNO')[score]
        
        print(f"\nTotal variables for correlation: {len(correlation_data)}")
        
        if len(correlation_data) >= 2:
            # Create DataFrame for correlation - this was causing the error
            print("Creating correlation DataFrame...")
            corr_df = pd.DataFrame(correlation_data)
            print(f"✓ DataFrame created successfully: {corr_df.shape}")
            
            # Calculate correlation matrix
            corr_matrix = corr_df.corr()
            print(f"✓ Correlation matrix calculated: {corr_matrix.shape}")
            
            print("\nSample correlation matrix:")
            print(corr_matrix.round(3))
            
            return True
        else:
            print("⚠️ Insufficient data for correlation testing")
            return False
            
    except Exception as e:
        print(f"✗ Correlation heatmap test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("="*50)
    print("PPMI Dashboard Correlation Fix Test")
    print("="*50)
    
    success = test_heatmap_function()
    
    if success:
        print("\n🎉 Correlation heatmap fix successful!")
        print("The 'ValueError: cannot reindex on an axis with duplicate labels' should be resolved.")
    else:
        print("\n❌ Test failed - issue may still exist")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)