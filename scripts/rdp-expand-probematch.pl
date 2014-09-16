use strict;
use Template;
use Getopt::Long::Descriptive;
use File::Slurp;
use Data::Dumper;

use JSON::XS;

my $template_file = "rdpprobematch.awt.tt";
if (exists $ENV{KB_SERVICE_DIR})
{
    $template_file = "$ENV{KB_SERVICE_DIR}/$template_file";
}

my($opt, $usage) = describe_options("%c %o primer-file query-file",
                                    ["output|o=s", "Write output to this file"],
                                    ["dist|n=s", "Give a max distance", { default => 0 }],
                                    ["token|t=s", "Data authentication token"]);

my $templ = Template->new({ ABSOLUTE => 1 });

my $primer_handle_file = shift;
my $query_handle_file = shift;

my $primer_handle = decode_json(scalar read_file($primer_handle_file));
my $query_handle = decode_json(scalar read_file($query_handle_file));

my $primer_file = $primer_handle->{file_name};
my $query_file = $query_handle->{file_name};

my $jobname = "rdp-probematch";
my $user = "username";
my $shock_url = $primer_handle->{url};
$shock_url =~ s,^http://,,;

my $outfile_name = $jobname . ".txt";

my $params = join(" ", -n => $opt->dist, -o => $outfile_name);

my $project = "project";

my %vars = (parameters => $params,
            primer_file => $primer_file,
            query_file => $query_file,
            output_file => $outfile_name,
            primer_handle => $primer_handle,
            query_handle => $query_handle,
            jobname => $jobname,
            user => $user,
            shockurl => $shock_url,
            project => $project,
            token => $opt->token);

if ($opt->output)
{
    open(OUT, ">", $opt->output) or die "Cannot open " . $opt->output . ": $!";
    $templ->process($template_file, \%vars, \*OUT)
        || die $templ->error();
    close(OUT);
}
else
{
    $templ->process($template_file, \%vars)
        || die $templ->error();
}
