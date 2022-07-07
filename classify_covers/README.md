
# Classify book covers as a catagory

* Download Images from s3
* Get `existing.json`
* Get `books.csv`


This is how to download the images using the aws CLI
```
aws s3 cp --recursive s3://<bucket>/<folder> <local_folder> 
```

> If `fatal error: Unable to locate credentials` then run first

```
aws configure 
```

## Scripts

* `prepare_images` moves the raw images into the correct directory structure for tensorflow. The images are also preprocessed, e.g they are cropped to remove white space.
* `classify` This runs the tensorflow CNN