# -*- mode: ruby -*-
# vi: set ft=ruby :

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.
Vagrant.configure(2) do |config|
  # Every Vagrant development environment requires a box. You can search for
  # boxes at https://atlas.hashicorp.com/search.
  config.vm.box = "ubuntu/xenial64"
  # set up network ip and port forwarding
  config.vm.network "forwarded_port", guest: 5000, host: 5000, host_ip: "127.0.0.1"
  config.vm.network "private_network", ip: "192.168.33.10"

  # Windows users need to change the permissions explicitly so that Windows doesn't
  # set the execute bit on all of your files which messes with GitHub users on Mac and Linux
  # config.vm.synced_folder "./", "/vagrant", owner: "vagrant", mount_options: ["dmode=775,fmode=664"]

  config.vm.provider "virtualbox" do |vb|
    # Customize the amount of memory on the VM:
    vb.memory = "512"
    vb.cpus = 1
    # Fixes some DNS issues on some networks
    vb.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
    vb.customize ["modifyvm", :id, "--natdnsproxy1", "on"]
  end

  # Copy your .gitconfig file so that your git credentials are correct
  if File.exists?(File.expand_path("~/.gitconfig"))
    config.vm.provision "file", source: "~/.gitconfig", destination: "~/.gitconfig"
  end

  # Copy your ssh keys for github so that your git credentials work
  if File.exists?(File.expand_path("~/.ssh/id_rsa"))
    config.vm.provision "file", source: "~/.ssh/id_rsa", destination: "~/.ssh/id_rsa"
  end

  # Copy your .vimrc file so that your VI editor looks right
  if File.exists?(File.expand_path("~/.vimrc"))
    config.vm.provision "file", source: "~/.vimrc", destination: "~/.vimrc"
  end

  # Enable provisioning with a shell script. Additional provisioners such as
  # Puppet, Chef, Ansible, Salt, and Docker are also available. Please see the
  # documentation for more information about their specific syntax and use.
  config.vm.provision "shell", inline: <<-SHELL
    apt-get update
    # Python 2
    apt-get install -y git python-pip python-dev build-essential
    # Python 3
    # apt-get install -y git tree python3-dev python3-pip python3-venv
    apt-get -y autoremove
    # Install app dependencies
    cd /vagrant
    sudo pip install -r requirements.txt
    cd
  SHELL

  # ######################################################################
  # # Add MySQL docker container
  # ######################################################################
  # # docker run -d --name mariadb -p 3306:3306 -v mysql_data:/var/lib/mysql -e MYSQL_ROOT_PASSWORD=passw0rd mariadb
  # config.vm.provision "docker" do |d|
  #   d.pull_images "mariadb"
  #   d.run "mariadb",
  #     args: "--restart=always -d --name mariadb -p 3306:3306 -v mysql_data:/var/lib/mysql -e MYSQL_ROOT_PASSWORD=passw0rd"
  # end

  ######################################################################
  # Add PostgreSQL docker container
  ######################################################################
  # docker run -d --name postgres -p 5432:5432 -v postgresql_data:/var/lib/postgresql/data postgres
  config.vm.provision "docker" do |d|
    d.pull_images "postgres"
    d.run "postgres",
       args: "-d --name postgres -p 5432:5432 -v postgresql_data:/var/lib/postgresql/data"
  end

  # Create the database after Docker is running
  config.vm.provision "shell", inline: <<-SHELL
    # Wait for mariadb to come up
    echo "Waiting 20 seconds for PostgreSQL to start..."
    sleep 20
    cd /vagrant
    docker exec postgres psql -U postgres -c "CREATE DATABASE development;"
    python manage.py development
    docker exec postgres psql -U postgres -c "CREATE DATABASE test;"
    python manage.py test
    cd
  SHELL

end
