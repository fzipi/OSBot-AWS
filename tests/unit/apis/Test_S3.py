import os
import unittest
from   aws.s3 import S3


class Test_S3(unittest.TestCase):
    def setUp(self):
        self.s3 = S3()
        assert self.s3.__class__.__name__ == 'S3'
        self.temp_file_name     = "aaa.txt"
        self.temp_file_contents = "some contents"
        self.test_bucket        = "gs-team-tests"
        self.test_folder        = "dinis"

    def _test_file(self):
        temp_file = os.path.abspath(self.temp_file_name)
        with open(temp_file, "w+") as f:
            f.write(self.temp_file_contents)
        assert os.path.isfile(temp_file) is True
        return temp_file

    def test_buckets       (self):
        names = self.s3.buckets()
        assert "gs-logs-pb" in names
        assert len(names) > 6

    def test_find_files    (self):
        test_bucket = "gs-logs-pb"
        prefix      = 'akamai'
        filter      = 'waf'
        files       = self.s3.find_files(test_bucket, prefix, filter)
        assert len(files) > 10


    def test_file_contents_delete_exists_upload   (self):
        key       = os.path.join(self.test_folder, self.temp_file_name)             # key is folder + file
        bucket    = self.test_bucket                                                # target bucket
        temp_file = self._test_file()                                               # create test test

        assert self.s3.file_exists(bucket, key                        ) is False    # confirm file doesn't exist (in s3)
        assert self.s3.file_upload(temp_file, bucket, self.test_folder) == key     # upload file (create it in s3)
        assert self.s3.file_exists(bucket, key                        ) is True     # confirm file exists (in s3)

        assert self.s3.file_contents(bucket, key) == self.temp_file_contents        # confirm file contents are expected

        assert self.s3.file_delete(bucket, key                        ) is True     # delete file
        assert self.s3.file_exists(bucket, key                        ) is False    # confirm file doesn't exist (in s3)

        os.remove(temp_file)                                                        # delete test file

    def test_file_create_from_string(self):
        file_contents = 'some test'
        bucket        = self.test_bucket                                                        # target bucket
        key           = os.path.join(self.test_folder, 'some-temp-file.txt')                    # key is folder + file

        assert self.s3.file_exists            (bucket, key               ) is False             # confirm file doesn't exist in s3
        assert self.s3.file_create_from_string(file_contents, bucket, key) is True              # create file in s3 (from string)
        assert self.s3.file_exists            (bucket, key               ) is True              # confirm file exists
        assert self.s3.file_contents          (bucket, key               ) == file_contents     # confirm file contents match
        assert self.s3.file_delete            (bucket, key               ) is True              # delete file

    def test_file_move(self):
        file_contents = 'some test'

        src_bucket  = self.test_bucket
        src_key     = self.test_folder + '/src_file.txt'
        dest_bucket = self.test_bucket
        dest_key    = self.test_folder + '/dest_file.txt'

        assert self.s3.file_create_from_string(file_contents, src_bucket, src_key              ) is True

        assert self.s3.file_exists            (src_bucket   , src_key                          ) is True
        assert self.s3.file_exists            (dest_bucket  , dest_key                         ) is False

        assert self.s3.file_move              (src_bucket   , src_key   , dest_bucket, dest_key) is True

        assert self.s3.file_exists            (src_bucket   , src_key                          ) is False
        assert self.s3.file_exists            (dest_bucket  , dest_key                         ) is True

        assert self.s3.file_contents          (dest_bucket  , dest_key                         ) == file_contents
        assert self.s3.file_delete            (src_bucket   , src_key                          ) is True
        assert self.s3.file_delete            (dest_bucket  , dest_key                         ) is True

if __name__ == '__main__':
    unittest.main()