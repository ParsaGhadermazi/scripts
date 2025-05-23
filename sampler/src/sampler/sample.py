import click
import pandas as pd
import json
import pathlib
import glob

def sampler(
            profiles:list,
            pair_mapping:dict,
            n_samples:int = 1000,
            )->pd.DataFrame:
    """
    from all possible pairs of profiles.
    Args:
        profiles: The list of pathes to all profiles.
        pair_mapping: a dictionary that maps a pair of profiles to their grouings.
    Returns:
        A pandas dataframe of the sampled pairs.
    """
    locations={x.name:str(x) for x in profiles}
    df=pd.DataFrame({"pair":pair_mapping.keys(), "group":pair_mapping.values()})
    df=df.groupby("group").sample(n_samples,replace=False)
    df["profile_1"]=df["pair"].str.split("|").str[0].apply(lambda x: locations.get(x,None))
    df["profile_2"]=df["pair"].str.split("|").str[1].apply(lambda x: locations.get(x,None))
    df.dropna(inplace=True)
    return df[["profile_1","profile_2","group"]].reset_index(drop=True)
    

@click.group()
def cli():
    """Compare SNV profiles and analyze strain sharing statistics."""
    pass

@cli.command('sample')
@click.option('--profiles', type=str, required=True, help='Paths to the inStrain profiles.')
@click.option('--pair_mapping', type=click.Path(exists=True), required=True, help='Path to the pair mappin json file.')
@click.option('--n_samples', type=int, default=1000, help='Number of samples to draw.')
@click.option('--output_file', type=click.Path(), required=True, help='Path to save the sampled pairs as a CSV file.')
def sample_command(profiles: list, pair_mapping: str, n_samples: int, output_file: str):
    """Sample pairs of profiles from all possible pairs."""
    with open(pair_mapping, "r") as f:
        pair_mapping = json.load(f)
    
    profiles = [pathlib.Path(x) for x in glob.glob(profiles)]
    df = sampler(
        profiles=profiles,
        pair_mapping=pair_mapping,
        n_samples=n_samples
    )
    df.to_csv(output_file, index=False)
    click.echo(f"Sampled pairs saved to {output_file}")

if __name__ == '__main__':
    cli()