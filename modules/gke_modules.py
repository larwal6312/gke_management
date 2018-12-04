def logging():
    import logging
    logger = logging.getLogger('logger')
    error_file = logging.FileHandler('error.log')
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    error_file.setFormatter(formatter)
    logger.addHandler(error_file)
    logger.setLevel(logging.WARNING)
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(formatter)
    logger.addHandler(consoleHandler)
    return logger

def backup_list(logger, s3_access, s3_key):
    import datetime
    import os
    Bucket = "s3://gannett-app-ops/wordpress/"
    Date = datetime.date.today().strftime("%Y%m%d")
    print("Building list of latest backups")
    os.system("s3cmd --access_key=%s --secret_key=%s ls %s | grep %s | grep -v stage > backup.list" %(s3_access, s3_key, Bucket, Date))
    if not os.path.isfile('backup.list'):
        logger.error("backup.list file not found, Script cold not finish")
        sys.exit(1)
    else:
        pass

    bck_list_size = os.stat('backup.list')

    if bck_list_size.st_size > 0:
        pass
    else:
        logger.error("backup.list size is null, Script could not finish")
        sys.exit(1)

def find_wp_gke():
    import os
    import json
    print("Finding wordpress pods in GKE")
    podList = []
    os.system("kubectl -o=json get pods > pods.json")
    with open('pods.json', 'r')as f:
        item_dict = json.load(f)
        podCount = len(item_dict['items'])
        realPodCount = podCount - 1
        f.closed
    count = 0
    while realPodCount >= count:
        with open ('pods.json', 'r') as f:
            json_dict = json.load(f)
            podName = str(json_dict['items'][count]['metadata']['name'])
            f.closed
        if "wordpress" in podName:
            podList.append('%s' %(podName))
            count += 1
        else:
            count += 1
            pass
    print podList
    return podList

def backup_check(podList, logger):
    open('error.log', 'w').close()
    pods = []
    failedBackups = 0
    sfBackup = False
    dbBackup = False
    sfValid = False
    dbValid = False
    for value in podList:
        name = value.split("-")[0]
        pods.append('%s' %(name))
    print("Starting backup check!")
    for site in pods:
        siteFilesCheck = (site, "docker-files")
        siteDBCheck = (site, "docker-db")
        print ("Verifying backups for %s" %(site))
        with open ('backup.list', 'r') as f:
            for line in f:
                if all (s in line for s in siteFilesCheck):
                    sfBackup = line
                if all (s in line for s in siteDBCheck):
                    dbBackup = line
        f.closed
        if sfBackup != False:
            sfColumns = sfBackup.split()
            sfSize = int(sfColumns[2])
            if sfSize >= 20:
                sfValid = True
            else:
                sfValid = False
        if dbBackup != False:
            dbColumns = dbBackup.split()
            dbSize = int(dbColumns[2])
            if dbSize >= 20:
                dbValid = True
            else:
                dbValid = False
        if not any ((dbBackup, sfBackup)):
            logger.error("No backups found for %s. Manually verify backups" %(site))
            failedBackups += 1
        elif ((sfBackup != False and dbBackup != False and sfValid == False and dbValid == False)):
            logger.error("Site File backup size and DB backup size is not valid for %s. Manually verify backup." %(site))
        elif ((sfBackup != False and dbValid == True and sfValid == False)):
            logger.error("Site File backup size is not valid for %s. Manually verify backup.\nDB backup is valid %s" %(site, site))
            failedBackups += 1
        elif ((sfBackup == False and dbValid == True)):
            logger.error("Site File backup is missing for %s. Manually verify backup.\nDB backup is valid for %s" %(site, site))
            failedBackups += 1
        elif ((dbBackup != False and sfValid == True and dbValid == False)):
            logger.error("DB backup size is not valid for %s. Manually verify backup.\nSite file backup is valid for %s" %(site, site))
            failedBackups += 1
        elif ((dbBackup == False and sfValid == True)):
            logger.error("DB backup is missing for %s. Manually verify backup.\nSite file backup is valid for %s" %(site, site))
            failedBackups += 1
        elif ((sfValid, dbValid)):
            print("Backups for are valid for %s" %(site))
    return failedBackups
